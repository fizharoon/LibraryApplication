from flask import Flask, render_template, request
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/librarian')
def librarian():
    return None

if __name__ == '__main__':
    app.run(debug=True)