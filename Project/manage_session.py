from flask import abort, redirect, render_template, request, session

from Project import app
from Project.dbconn import conn


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
                return abort(404)
            else:
                session['l_librariankey'] = res[0][0]
                session['l_name'] = res[0][1]
        else:
            session['u_userkey'] = res[0][0]
            session['u_name'] = res[0][1]

        return res
    return render_template('login.html')