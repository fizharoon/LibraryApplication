import sqlite3
from sqlite3 import Error

import flask
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from flask_login import LoginManager

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

@app.route('/search/<keyword>', methods=['GET'])
def searchByTitle(keyword):
    res = {}
    try:
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
            hb_bookkey = b_bookkey AND
            b_title LIKE ?
        UNION
        SELECT b_title, b_pages, bs_rating, e_format, 'Available'
        FROM books, book_stats, ebooks
        WHERE
            bs_bookkey = b_bookkey AND
            e_bookkey = b_bookkey AND
            b_title LIKE ?;"""
        parameter = '%'+keyword+'%'
        args = [parameter, parameter]

        cur = conn.cursor()
        cur.execute(sql, args)

        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

# @app.route('/grades/<name>', methods=['PUT'])
# def update_grade(name):
#     student = Grade.query.get(name)
#     student.name = request.json['name']
#     student.grade = request.json['grade']
#     db.session.commit()
#     return {student.name: student.grade}
@app.route('/checkouthardcopy', methods=['PUT'])
def checkoutHardCopy():
    try:
        userkey = request.json['userkey']
        bookkey = request.json['bookkey']

        sql = """
            UPDATE hardcopy_books
            SET
                hb_userkey = ?,
                hb_codate = DATE()
            WHERE hb_bookkey = ?;"""

        args = [userkey, bookkey]
        conn.execute(sql, args)
        conn.commit()
        
    except Error as e:
        print(e)

@app.route('/checkoutebook', methods=['POST'])
def checkoutEbook():
    try:
        userkey = request.json['userkey']
        bookkey = request.json['bookkey']

        sql = """
            INSERT INTO ebook_checkout (ec_bookkey, ec_userkey, ec_codate)
            SELECT e_bookkey, ?, DATE()
            FROM ebooks
            WHERE e_bookkey = ?;"""

        args = [userkey, bookkey]
        conn.execute(sql, args)
        conn.commit()

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

    except Error as e:
        print(e)

@app.route('/usercheckouts/<userkey>', methods=['GET'])
def getUserCheckouts(userkey):
    res = {}

    try:
        sql = """
            SELECT b_title, hb_type as book_format
            FROM hardcopy_books, books
            WHERE
                hb_userkey = ? AND
                hb_bookkey = b_bookkey
            UNION
            SELECT b_title, e_format
            FROM ebook_checkout, ebooks, books
            WHERE
                e_bookkey = b_bookkey AND
                ec_bookkey = e_bookkey AND
                ec_userkey = ? AND
                DATE(ec_codate, e_loanperiod) > DATE();"""

        cur = conn.cursor()
        cur.execute(sql, [userkey, userkey])

        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

@app.route('/userholds/<userkey>', methods=['GET'])
def getUserHolds(userkey):
    res = {}

    try:
        sql = """
            SELECT b_title, hb_type
            FROM holds, books, hardcopy_books
            WHERE
                h_userkey = ? AND
                h_bookkey = hb_bookkey AND
                h_bookkey = b_bookkey;"""

        cur = conn.cursor()
        cur.execute(sql, [userkey])

        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

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

@app.route('/usersearch/<name>', methods=['GET'])
def searchForUser(name):
    try:
        res = {}
        sql = """
            select * from user 
            where u_name LIKE ?"""

        cur = conn.cursor()
        cur.execute(sql, ['%'+name+'%'])

        res = cur.fetchall()

    except Error as e:
        print(e)

    return res

@app.route('/deleteuser', methods=['DELETE'])
def deleteUser():
    try:
        userkey = request.json['userkey']
        sql = """
            DELETE FROM user
            WHERE u_userkey = ?"""

        conn.execute(sql, [userkey])
        conn.commit()

    except Error as e:
        print(e)

@app.route('/createuser', methods=['POST'])
def createUser():
    try:
        name = request.json['name']
        username = request.json['username']
        password = request.json['password']
        address = request.json['address']
        phone = request.json['phone']
        sql = """
            INSERT INTO user VALUES ((SELECT max(u_userkey) FROM user)+1, 
                ?, ?, ?, ?, ?, ?)"""

        args = [name, username, password, session['librariankey'], address, phone]

        conn.execute(sql, args)
        conn.commit()
    
    except Error as e:
        print(e)

# @app.route('/updateuser/<attribute>')

@app.route('/deletebook')
def deleteBook():
    try:
        bookkey = request.json['bookkey']

        sql = """
            DELETE FROM books WHERE b_bookkey = ?"""

        # delete from hardcopy/ebook?

    except Error as e:
        print(e)

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/logout")
def logout():
    session["u_userkey"] = None
    session["u_name"] = None
    session["l_librariankey"] = None
    session["l_name"] = None
    return redirect(flask.url_for('home'))

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

            print(res)

            if not res:
                return flask.abort(404)
            else:
                session['l_librariankey'] = res[0][0]
                session['l_name'] = res[0][1]
                print(session['l_librariankey'])
        else:
            session['u_userkey'] = res[0][0]
            session['u_name'] = res[0][1]

        return res
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)