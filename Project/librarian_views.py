from sqlite3 import Error

from flask import render_template, request, session, make_response

from Project import app
from Project.dbconn import conn


@app.route('/getall', defaults={'sort': None})
@app.route('/getall/<sort>', methods=['GET'])
def getAllBooks(sort):
    res = {}
    try:
        arg = ''
        if not sort or sort == 'title':
            arg = 'b_title ASC'
        elif sort == 'rating':
            arg = 'bs_rating DESC'
        elif sort == 'pagecount':
            arg = 'b_pages'

        sql = """
            SELECT b_title, b_pages, bs_rating, hb_type,
                CASE
                WHEN hb_userkey IS NULL
                    THEN 'Available'
                ELSE 'Unavailable'
                END availability
            FROM books, book_stats, hardcopy_books
            WHERE
                bs_bookkey = b_bookkey AND
                hb_bookkey = b_bookkey
            UNION
            SELECT b_title, b_pages, bs_rating, e_format, 'Available'
            FROM books, book_stats, ebooks
            WHERE
                bs_bookkey = b_bookkey AND
                e_bookkey = b_bookkey
            ORDER BY {};""".format(arg)

        cur = conn.cursor()
        cur.execute(sql)

        
        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

@app.route('/bookinfo/<bookkey>', methods=['GET'])
def getBookInfo(bookkey):
    res = {}
    names = ['b_bookkey', 'b_title', 'b_pages', 'b_rating', 'b_format', 'b_checkedOutBy', 'b_totalholds', 'b_totalcheckouts']
    cur = conn.cursor()

    try:
        sql = """
            SELECT * FROM book_info
            WHERE b_bookkey = ?"""
        cur.execute(sql, [bookkey])
        for name, attribute in zip(names, cur.fetchone()):
            res.update({name: attribute})
        
    except Error as e:
        print(e)

    return render_template('bookinfo.html', book=res)

@app.route('/checkouthistory', methods=['GET'])
def getCheckoutHistory():
    res = {}

    try:
        sql = """
            SELECT past.b_title, past_checkouts + current_checkouts as total_checkouts
            FROM
                (SELECT count() as past_checkouts, b_bookkey, b_title
                FROM books, checkout_history
                WHERE b_bookkey = ch_bookkey
                GROUP BY b_bookkey
                ) past,
                (SELECT count() as current_checkouts, b_bookkey
                FROM books, hardcopy_books
                WHERE
                    b_bookkey = hb_bookkey AND
                    hb_codate NOT NULL
                GROUP BY b_bookkey
                ) present
            GROUP BY past.b_bookkey
            UNION
            SELECT b_title, count() as total_checkouts
            FROM books, ebook_checkout
            WHERE b_bookkey = ec_bookkey
            GROUP BY b_bookkey
            ORDER BY total_checkouts DESC;"""

        cur = conn.cursor()
        cur.execute(sql)

        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

@app.route('/usersearch', methods=['GET'])
def searchForUser():
    try:
        name = request.args.get('name')
        res = []
        names = ['u_userkey', 'u_name', 'u_username', 'u_password', 'u_librariankey', 'u_address', 'u_phone', 'u_pastcheckouts', 'u_curcheckouts', 'u_curholds']

        sql = """
            select * from user_info
            where u_name LIKE ?"""

        cur = conn.cursor()
        cur.execute(sql, ['%'+name+'%'])

        for user in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, user):
                cur.update({name: attribute})
            res.append(cur)

    except Error as e:
        print(e)

    return res

@app.route('/deleteuser', methods=['DELETE'])
def deleteUser():
    try:
        userkey = request.json['u_userkey']
        sql = """
            DELETE FROM user
            WHERE u_userkey = ?"""

        conn.execute(sql, [userkey])
        conn.commit()

        return {}, 204

    except Error as e:
        print(e)

@app.route('/createuser', methods=['POST'])
def createUser():
    try:
        cur = conn.cursor()
        newUserKey = cur.execute("""
            SELECT max(userkey)
            FROM
                (SELECT max(u_userkey) as userkey FROM user
                UNION
                SELECT max(ch_userkey) as userkey FROM checkout_history
                UNION
                SELECT max(ec_userkey) as userkey FROM ebook_checkout
                UNION
                SELECT max(h_userkey) as userkey FROM holds
                )""").fetchone()[0] + 1

        name = request.json['u_name']
        username = request.json['u_username']
        password = request.json['u_password']
        address = request.json['u_address']
        phone = request.json['u_phone']

        sql = """
            INSERT INTO user VALUES
                (?, ?, ?, ?, ?, ?, ?)"""

        args = [newUserKey, name, username, password, session['l_librariankey'], address, phone]

        conn.execute(sql, args)
        conn.commit()

        return {newUserKey: args[1:]}, 201
    
    except Error as e:
        print(e)

@app.route('/updateuser/<userkey>', methods=['PUT'])
def updateUser(userkey):
    try:
        user_attributes = ['u_name', 'u_username', 'u_password', 'u_address', 'u_phone']
        data = request.json
        args = []

        cur = conn.cursor()

        for attribute in user_attributes:
            if data[attribute] != "":
                args.append(data[attribute])
            else:
                args.append(cur.execute('SELECT {} FROM user WHERE u_userkey = {}'.format(attribute, userkey)).fetchone()[0])
        
        args.append(userkey)

        sql = """
            UPDATE user
                SET u_name = ?,
                    u_username = ?,
                    u_password = ?,
                    u_address = ?,
                    u_phone = ?
                WHERE u_userkey = ?"""
        conn.execute(sql, args)

        conn.commit()

        return {userkey: args}

    except Error as e:
        print(e)

@app.route('/deletebook', methods=['DELETE'])
def deleteBook():
    try:
        bookkey = request.json['b_bookkey']
        sqls = ["DELETE FROM books WHERE b_bookkey = ?;",
            "DELETE FROM book_stats WHERE bs_bookkey = ?",
            "DELETE FROM hardcopy_books WHERE hb_bookkey = ?;",
            "DELETE FROM ebooks WHERE e_bookkey = ?;"]

        for sql in sqls:
            conn.execute(sql, [bookkey])
        conn.commit()

    except Error as e:
        print(e)

    return {}, 204

@app.route('/addebook', methods=['POST'])
def add_eBook():
    try:
        cur = conn.cursor()
        cur.execute("SELECT max(b_bookkey) FROM books")

        b_bookkey = cur.fetchone()[0] + 1
        b_title = request.json['b_title']
        b_pages = request.json['b_pages']
        b_librarian = session['l_librariankey']
        bs_rating = request.json['bs_rating']
        bs_reviews = request.json['bs_reviews']
        bs_price = request.json['bs_price']

        conn.execute("INSERT INTO books VALUES(?, ?, ?, ?)",
            [b_bookkey, b_title, b_pages, b_librarian])
        conn.execute("INSERT INTO book_stats VALUES(?, ?, ?, ?)",
            [b_bookkey, bs_rating, bs_reviews, bs_price])

        e_loanperiod = request.json['e_loanperiod']
        e_format = request.json['e_format']

        conn.execute("INSERT INTO ebooks VALUES(?, ?, ?)",
            [b_bookkey, e_loanperiod, e_format])
        
        conn.commit()
    except Error as e:
        print(e)

    return request.json

@app.route('/addhardcopybook', methods=['POST'])
def add_hardcopyBook():
    try:
        cur = conn.cursor()
        cur.execute("SELECT max(b_bookkey) FROM books")

        b_bookkey = cur.fetchone()[0] + 1
        b_title = request.json['b_title']
        b_pages = request.json['b_pages']
        b_librarian = session['l_librariankey']
        bs_rating = request.json['bs_rating']
        bs_reviews = request.json['bs_reviews']
        bs_price = request.json['bs_price']

        conn.execute("INSERT INTO books VALUES(?, ?, ?, ?)",
            [b_bookkey, b_title, b_pages, b_librarian])
        conn.execute("INSERT INTO book_stats VALUES(?, ?, ?, ?)",
            [b_bookkey, bs_rating, bs_reviews, bs_price])

        hb_type = request.json['hb_type']

        conn.execute("INSERT INTO hardcopy_books VALUES(?, NULL, NULL, ?)",
            [b_bookkey, hb_type])
        
        conn.commit()
    except Error as e:
        print(e)

    return request.json