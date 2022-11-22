from sqlite3 import Error

from flask import abort, jsonify, make_response, request, session

from Project import app
from Project.dbconn import conn


@app.route('/search', defaults={'sort': None})
@app.route('/search/<sort>', methods=['GET'])
def searchByTitle(sort):
    keyword = request.args.get('keyword')

    if not sort or sort == 'title':
        sort = 'b_title'
    elif sort == 'ratingdec':
        sort = 'b_rating DESC'

    res = []
    names = ['b_bookkey', 'b_title', 'b_pages', 'b_rating', 'b_type', 'b_availability', 'isCheckedOut', 'isHeld']
    try:
        if session.get('u_userkey'):
            sql = """
                SELECT book_search.*,
                    CASE
                    WHEN SQ1.b_userkey IS NULL
                        THEN FALSE
                    ELSE TRUE
                    END isCheckedOut,
                    CASE
                    WHEN SQ2.h_userkey IS NULL
                        THEN FALSE
                    ELSE TRUE
                    END isHeld
                FROM book_search LEFT JOIN
                    (SELECT * FROM user_checkouts WHERE b_userkey = ?) SQ1
                        ON book_search.b_bookkey = SQ1.b_bookkey
                    LEFT JOIN
                    (SELECT * FROM holds WHERE h_userkey = ? AND h_status = 'ACTIVE') SQ2
                        ON book_search.b_bookkey = SQ2.h_bookkey
                WHERE book_search.b_title LIKE ?
                ORDER BY {};""".format(sort)
            parameter = '%'+keyword+'%'
            args = [session['u_userkey'], session['u_userkey'], parameter]
        else:
            sql = """
                SELECT * FROM book_search WHERE b_title LIKE ?
                ORDER BY {}""".format(sort)
            args = ['%'+keyword+'%']

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

    return jsonify(res)

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
            sql2 = """
                UPDATE holds
                SET h_status = 'FILLED'
                WHERE
                    h_userkey = ? AND
                    h_bookkey = ?"""
            response = {bookkey: cur.execute("SELECT * FROM hardcopy_books WHERE hb_bookkey = {}".format(bookkey)).fetchone()}

        args = [userkey, bookkey]
        conn.execute(sql, args)
        if sql2:
            conn.execute(sql2, args)
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
        return abort(404)

    
@app.route('/hold', methods=['POST'])
def placeHold():
    try:
        userkey = session['u_userkey']
        bookkey = request.json['bookkey']
        sql = """
            INSERT INTO holds (h_bookkey, h_userkey, h_holdplaced, h_status)
            VALUES (?, ?, date(), 'ACTIVE');"""

        conn.execute(sql, [bookkey, userkey])
        conn.commit()

        return {}, 201

    except Error as e:
        print(e)
        return make_response(str(e), 403)

@app.route('/cancelhold', methods=['PUT'])
def cancelHold():
    try:
        userkey = session['u_userkey']
        bookkey = request.json['bookkey']
        sql = """
            UPDATE holds
            SET h_status = 'CANCELLED'
            WHERE
                h_bookkey = ? AND
                h_userkey = ?;"""

        conn.execute(sql, [bookkey, userkey])
        conn.commit()

        return {}, 201

    except Error as e:
        print(e)
        return make_response(str(e), 403)

@app.route('/usercheckouts', methods=['GET'])
def getUserCheckouts():
    res = []
    names = ['b_userkey', 'b_bookkey', 'b_title', 'b_format', 'b_checkout', 'b_remaining']

    try:
        sql = """
            SELECT * FROM user_checkouts WHERE b_userkey = ?
            ORDER BY b_checkout"""

        cur = conn.cursor()
        cur.execute(sql, [session['u_userkey']])

        for book in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, book):
                cur.update({name: attribute})
            res.append(cur)

    except Error as e:
        print(e)

    return jsonify(res)

@app.route('/userholds', methods=['GET'])
def getUserHolds():
    res = []
    names = ['b_userkey', 'b_bookkey', 'b_title', 'b_holdplaced', 'b_availability']

    try:
        sql = """
            SELECT * FROM user_holds WHERE b_userkey = ?;"""

        cur = conn.cursor()
        cur.execute(sql, [session['u_userkey']])

        for book in cur.fetchall():
            cur = {}
            for name, attribute in zip(names, book):
                cur.update({name: attribute})
            res.append(cur)

    except Error as e:
        print(e)

    return jsonify(res)