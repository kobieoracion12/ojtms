import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from markupsafe import escape


app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM accounts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_type' in session == 'admin':
        return redirect(url_for('home'))
    if 'user_type' in session == 'user':
        return redirect(url_for('student'))

    error = None
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_pass = request.form['user_pass']
        validate_user = validate(user_name, user_pass)
        if validate_user == False:
            error = 'Invalid Credentials Please Try Again'
            return render_template('index.html', error=error)
        else:
            session['user_type'] = 'user'
            session['user_name'] = request.form['user_name']
            if session['user_type'] == 'admin':
                return redirect(url_for('home'))
            elif session['user_type'] != 'admin':
                return redirect(url_for('student'))

# Create a separate login for admin and user
    return render_template('index.html', error=error)

def query_db(query, args=(), one=False):
    cur = get_db_connection().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def validate(user_name, user_pass):
    conn = get_db_connection()
    user = query_db('SELECT * FROM accounts WHERE user_name = ?',
                    [user_name], one=True)

    return False if user is None else check_password(user['user_pass'], user_pass)

def check_password(user_password, user_pass):
    return user_pass == user_password

@app.route('/logout')
def logout():
    session.pop(('user_name'), None,)
    session.pop(('user_type'), None,)
    return redirect(url_for('index'))

"""Admin Dashboard"""
@app.route('/adviser-home')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    property_count = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    property_counts = cur.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    posts = conn.execute('SELECT * FROM accounts').fetchall()
    change = str(property_count)
    changes = str(property_counts)
    cur.close()
    conn.close()
    return render_template('admin/adviser-home.html', posts=posts, change=change, changes=changes)

"""Pending"""
@app.route('/adviser-adviser')
def adviser():
    return render_template('admin/adviser.html')


"""Pending Card"""
@app.route('/card')
def card():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM subjects ORDER BY date_submit DESC').fetchall()
    conn.close()
    return render_template('admin/card.html', posts=posts)


"""Student Data Edit"""
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_add = request.form['email_add']
        contact_no = request.form['contact_no']
        user_name = request.form['user_name']

        conn = get_db_connection()
        conn.execute('UPDATE accounts SET first_name = ?, last_name = ?, email_add = ?, contact_no = ?, user_name = ?'
                     ' WHERE id = ?',
                     (first_name, last_name, email_add, contact_no, user_name, id))
        conn.commit()
        conn.close()
        return redirect(url_for('data'))
    return render_template('admin/profile.html', post=post)


"""Student Data Delete"""
@app.route('/<int:id>/delete', methods=('GET', 'POST'))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM accounts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('data'))


"""Student Data Table"""
@app.route('/data')
def data():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM accounts  ORDER BY acc_created DESC').fetchall()
    conn.close()
    return render_template('admin/data.html', posts=posts)


"""Teacher Registration"""
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_add = request.form['email_add']
        contact_no = request.form['contact_no']
        user_name = request.form['user_name']
        user_pass = request.form['user_pass']
        session['user_type'] = 'admin'

        conn = get_db_connection()
        conn.execute('INSERT INTO accounts (first_name, last_name, email_add, contact_no, user_name, user_pass, user_type) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (first_name, last_name, email_add, contact_no, user_name, user_pass, session['user_type']))
        conn.commit()
        conn.close()
        return redirect(url_for('register'))
    return render_template('register.html')


"""Add Student Data"""
@app.route('/students', methods=('GET', 'POST'))
def students():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_add = request.form['email_add']
        contact_no = request.form['contact_no']
        user_name = request.form['user_name']
        user_pass = request.form['user_pass']
        hours = request.form['hours']
        sub_code = request.form['sub_code']
        session['user_type'] = 'user'

        conn = get_db_connection()
        conn.execute('INSERT INTO accounts (first_name, last_name, email_add, contact_no, user_name, user_pass, hours, sub_code, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (first_name, last_name, email_add, contact_no, user_name, user_pass, hours, sub_code, session['user_type']))
        conn.commit()
        conn.close()
        return redirect(url_for('data'))
    return render_template('admin/students.html')


"""Student Submit Report"""
@app.route('/students-students', methods=('GET', 'POST'))
def student():
    symbol = session['user_name']
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM accounts WHERE user_name = ?',[symbol]).fetchall()
    conn.close()

    if request.method == 'POST':
        user_name = session['user_name']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        hours_left = request.form['hours_left']
        details = request.form['details']

        conn = get_db_connection()
        conn.execute('INSERT INTO subjects (user_name, hours_left, first_name, last_name, details) VALUES (?, ?, ?, ?, ?)',
                         (user_name, hours_left, first_name, last_name, details))
        conn.commit()
        conn.close()
        return redirect(url_for('student'))
    return render_template('student/students.html', posts=posts)


"""Student Submission History"""
@app.route('/students-submissions')
def submissions():
    symbol = session['user_name']
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM subjects WHERE user_name = ? ORDER BY date_submit DESC ',[symbol]).fetchall()
    conn.close()
    return render_template('student/submissions.html', posts=posts)

"""End of Functions"""
app.run(host="localhost", debug=True)
