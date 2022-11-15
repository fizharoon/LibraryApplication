import sqlite3
from sqlite3 import Error

import flask
from flask import Flask, render_template, request, session, redirect
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def openConnection(dbFile):
    conn = None
    try:
        conn = sqlite3.connect(dbFile, check_same_thread=False)
    except Error as e:
        print(e)

    return conn

conn = openConnection('progbooks.db')

def closeConnection(conn):
    try:
        conn.close()
    except Error as e:
        print(e)

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

@app.route('/search', methods=['GET'])
def searchByTitle():
    keyword = request.args.get('keyword')
    res = []
    names = ['b_bookkey', 'b_title', 'b_pages', 'bs_rating', 'type', 'availability']
    try:
        sql = """
            SELECT b_bookkey, b_title, b_pages, bs_rating, hb_type,
            CASE
            WHEN hb_userkey IS NULL
                THEN 'Available'
            ELSE 'Unavailable'
            END availability
        FROM books, book_stats, hardcopy_books
        WHERE
            bs_bookkey = b_bookkey AND
            hb_bookkey = b_bookkey AND
            b_title LIKE ?
        UNION
        SELECT b_bookkey, b_title, b_pages, bs_rating, e_format, 'Available'
        FROM books, book_stats, ebooks
        WHERE
            bs_bookkey = b_bookkey AND
            e_bookkey = b_bookkey AND
            b_title LIKE ?
        ORDER BY b_title;"""
        parameter = '%'+keyword+'%'
        args = [parameter, parameter]

        cur = conn.cursor()
        cur.execute(sql, args)

        for book in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, book):
                cur.update({name: attribute})
            res.append(cur)

        # print(keyword)
        # print(res)

    except Error as e:
        print(e)

    return flask.jsonify(res)

@app.route('/bookinfo/<bookkey>', methods=['GET'])
def getBookInfo(bookkey):
    res = {}

    try:
        sql = """SELECT * FROM ebooks WHERE e_bookkey = ?"""
        cur = conn.cursor()
        cur.execute(sql, [bookkey])

        if cur.fetchall():
            sql = """SELECT count() as total_checkouts
                    FROM ebook_checkout
                    WHERE ec_bookkey = ?;"""
            cur.execute(sql, [bookkey])
            res.update({'total_checkouts': cur.fetchone()[0]})
        else:
            sql = """SELECT count() as total_holds
                FROM holds
                WHERE h_bookkey = ?;"""
            cur.execute(sql, [bookkey])
            res.update({'total_holds': cur.fetchone()[0]})
            sql = """SELECT count() as total_checkouts
                    FROM checkout_history
                    WHERE ch_bookkey = ?;"""
            cur.execute(sql, [bookkey])
            res.update({'total_checkouts': cur.fetchone()[0]})

        sql = """SELECT b_bookkey, b_title, b_pages, bs_rating, hb_type
            FROM books, book_stats, hardcopy_books
            WHERE
                bs_bookkey = b_bookkey AND
                hb_bookkey = b_bookkey AND
                b_bookkey = ?
            UNION
            SELECT b_bookkey, b_title, b_pages, bs_rating, e_format
            FROM books, book_stats, ebooks
            WHERE
                bs_bookkey = b_bookkey AND
                e_bookkey = b_bookkey AND
                b_bookkey = ?;"""
        cur.execute(sql, [bookkey, bookkey])

        book = cur.fetchone()
        res.update({'b_bookkey': book[0]})
        res.update({'b_title': book[1]})
        res.update({'b_pages': book[2]})
        res.update({'bs_rating': book[3]})
        res.update({'format': book[4]})
    except Error as e:
        print(e)

    return render_template('bookinfo.html', book=res)

@app.route('/checkout', methods=['PUT', 'POST'])
def checkout():
    try:
        userkey = session['u_userkey']
        bookkey = request.json['bookkey']

        sql = """SELECT * FROM ebooks WHERE e_bookkey = ?"""
        cur = conn.cursor()
        cur.execute(sql, [bookkey])

        response = {}

        if cur.fetchall():
            sql = """
            INSERT INTO ebook_checkout (ec_bookkey, ec_userkey, ec_codate)
            SELECT e_bookkey, ?, DATE()
            FROM ebooks
            WHERE e_bookkey = ?;"""
            response = {bookkey: cur.execute("SELECT * FROM ebook_checkout WHERE ec_bookkey = {}".format(bookkey)).fetchone()}
        else:
            sql = """
                UPDATE hardcopy_books
                SET
                    hb_userkey = ?,
                    hb_codate = DATE()
                WHERE hb_bookkey = ?;"""
            response = {bookkey: cur.execute("SELECT * FROM hardcopy_books WHERE hb_bookkey = {}".format(bookkey)).fetchone()}

        args = [userkey, bookkey]
        conn.execute(sql, args)
        conn.commit()

        return response, 201
        
    except Error as e:
        print(e)  

@app.route('/return', methods=['POST', 'PUT'])
def returnBook():
    try:
        bookkey = request.json['bookkey']
        args = [bookkey]

        sql = """
            INSERT INTO checkout_history (ch_bookkey, ch_userkey, ch_codate, ch_cidate)
            SELECT hb_bookkey, hb_userkey, hb_codate, DATE()
            FROM hardcopy_books
            WHERE hb_bookkey = ?;"""

        conn.execute(sql, args)

        sql = """
            UPDATE hardcopy_books
            SET
                hb_userkey = NULL,
                hb_codate = NULL
            WHERE hb_bookkey = ?;"""

        conn.execute(sql, args)

        conn.commit()

        return {}, 201

    except Error as e:
        print(e)
        return flask.abort(404)

@app.route('/hold', methods=['POST'])
def placeHold():
    try:
        userkey = flask.session['u_userkey']
        bookkey = request.json['bookkey']
        sql = """
            INSERT INTO holds (h_bookkey, h_userkey, h_holdplaced)
            VALUES (?, ?, date());"""

        conn.execute(sql, [bookkey, userkey])
        conn.commit()

        return {}, 201

    except Error as e:
        print(e)
        return flask.make_response(str(e), 403)

@app.route('/usercheckouts', methods=['GET'])
def getUserCheckouts():
    res = []
    names = ['b_bookkey', 'b_title', 'hb_type']

    try:
        sql = """
            SELECT b_bookkey, b_title, hb_type as book_format
            FROM hardcopy_books, books
            WHERE
                hb_userkey = ? AND
                hb_bookkey = b_bookkey
            UNION
            SELECT b_bookkey, b_title, e_format
            FROM ebook_checkout, ebooks, books
            WHERE
                e_bookkey = b_bookkey AND
                ec_bookkey = e_bookkey AND
                ec_userkey = ? AND
                DATE(ec_codate, e_loanperiod) > DATE();"""

        cur = conn.cursor()
        cur.execute(sql, [session['u_userkey'], session['u_userkey']])

        for book in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, book):
                cur.update({name: attribute})
            res.append(cur)

    except Error as e:
        print(e)

    return flask.jsonify(res)

@app.route('/userholds', methods=['GET'])
def getUserHolds():
    res = []
    names = ['b_bookkey', 'b_title', 'h_holdplaced', 'availability']

    try:
        sql = """
            SELECT b_bookkey, b_title, h_holdplaced,
                CASE
                WHEN hb_userkey IS NULL
                    THEN 'Available'
                ELSE 'Unavailable'
                END availability
            FROM books, holds LEFT OUTER JOIN
                (SELECT * FROM hardcopy_books WHERE hb_userkey IS NOT NULL)
                ON h_bookkey = hb_bookkey
            WHERE
                b_bookkey = h_bookkey AND
                h_userkey = ?;"""

        cur = conn.cursor()
        cur.execute(sql, [session['u_userkey']])

        for book in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, book):
                cur.update({name: attribute})
            res.append(cur)

    except Error as e:
        print(e)

    return flask.jsonify(res)

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
        names = ['u_userkey', 'u_name', 'u_username', 'u_password', 'u_librariankey', 'u_address', 'u_phone']

        sql = """
            select * from user 
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
        newUserKey = cur.execute("SELECT max(u_userkey) FROM user").fetchone()[0] + 1

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

        return {newUserKey: args[1:]}
    
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
        sql = """
            DELETE FROM books WHERE b_bookkey = ?;
            DELETE FROM hardcopy_books WHERE hb_bookkey = ?;
            DELETE FROM ebooks WHERE e_bookkey = ?;"""

        conn.execute(sql, [bookkey, bookkey, bookkey])
        conn.commit()

    except Error as e:
        print(e)

    return {}, 204

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/user', methods=['GET'])
def user():
    if session.get('l_librariankey'):
        return redirect('/librarian')
    if not session.get('u_userkey'):
        return redirect('/')
    return render_template('user.html')

@app.route('/librarian')
def librarian():
    if session.get('u_userkey'):
        return redirect('/user')
    if not session.get('l_librariankey'):
        return redirect('/')
    return render_template('librarian.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if session.get('u_userkey') or session.get('l_librariankey'):
            logout()

        username = request.json['username']
        password = request.json['password']
        sql = """
            SELECT * FROM user WHERE u_username = ? AND u_password = ?"""

        cur = conn.cursor()
        cur.execute(sql, [username, password])

        res = cur.fetchall()

        if not res:
            sql = """
                SELECT * FROM librarian WHERE l_username = ? AND l_password = ?"""

            cur = conn.cursor()
            cur.execute(sql, [username, password])

            res = cur.fetchall()

            if not res:
                return flask.abort(404)
            else:
                session['l_librariankey'] = res[0][0]
                session['l_name'] = res[0][1]
        else:
            session['u_userkey'] = res[0][0]
            session['u_name'] = res[0][1]

        return res
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)