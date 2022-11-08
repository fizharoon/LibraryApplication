from flask import Flask, render_template
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

@app.route('/getall', methods=['GET'])
def getAllBooks():
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
                hb_bookkey = b_bookkey
            UNION
            SELECT b_title, b_pages, bs_rating, e_format, 'Available'
            FROM books, book_stats, ebooks
            WHERE
                bs_bookkey = b_bookkey AND
                e_bookkey = b_bookkey
            ORDER BY b_title;"""
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

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)