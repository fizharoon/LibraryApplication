import sqlite3
from sqlite3 import Error


def openConnection(dbFile):
    conn = None
    try:
        conn = sqlite3.connect(dbFile, check_same_thread=False)
    except Error as e:
        print(e)

    return conn

def closeConnection(conn):
    try:
        conn.close()
    except Error as e:
        print(e)

conn = openConnection('Project/instance/progbooks.db')