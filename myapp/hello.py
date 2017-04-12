# -*- coding: utf-8 -*-
import os
import sqlite3
import time
import json
#import sys   #引用sys模块进来，并不是进行sys的第一次加载
#reload(sys)  #重新加载sys
#sys.setdefaultencoding('utf8')  ##调用setdefaultencoding函数
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, './data/myapp.db'),
    DEBUG=True,
    SECRET_KEY='\xc4\xda\xfea\x93@|f(\x9dr\xa2\xb0@%\xb6\x1fF"\xe4\x1a\xa3\xcf',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select title, text, created_at from entries order by id desc')
    entries = cur.fetchall()
    return render_template('home.html', entries=entries)

#登录
@app.route('/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != "admin":
            error = 'Invalid username'
        elif request.form['password'] != "admin":
            error = 'Invalid password'
        else:
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

#注销
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were Logged out')
    return redirect(url_for('index'))

#新增留言
@app.route('/add', methods=['POST'])
def add():
    #g.db = connect_db()
    db = get_db()
    if not session.get('username'):
        abort(401)
    db.execute('insert into entries (title, text) values (?,?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

#验证登录
def valid_login(username,password):
    if username == "admin" and password == "admin":
        return True
    else:
        return False

def log_the_user_in(username):
    session['username'] = username
    #return redirect(url_for('home'))
    return render_template('home.html')

@app.route('/home')
def home():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])

#后台管理
@app.route('/admin')
def admin():
    if session.get('admin_username') is None:
        return render_template('admin/login.html')
    return render_template('admin/admin.html')

#后台登录
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != "admin":
            error = 'Invalid username'
        elif request.form['password'] != "admin":
            error = 'Invalid password'
        else:
            session['admin_username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('admin'))
    return render_template('/admin/login.html', error = error)

#后台注销
@app.route('/admin/admin_logout',methods=['GET'])
def admin_logout():
    session.pop('admin_username',None)
    flash("注销成功")
    return redirect(url_for('admin_login'))

@app.route('/admin/admin_user',methods=['GET'])
def admin_user():
    db = get_db()
    cur = db.execute('select * from user order by user_id desc')
    entries = cur.fetchall()
    return render_template('/admin/user.html', entries=entries)

@app.route('/admin/admin_alist',methods=['GET'])
def admin_alist():
    db = get_db()
    cur = db.execute('select * from user order by user_id desc')
    entries = cur.fetchall()
    return json.dumps(entries)

@app.route('/admin/admin_user_delete/<int:id>',methods=['GET'])
def admin_user_delete(id):
    db = get_db()
    db.execute('delete from user where user_id = ?',[id])
    db.commit()
    flash('delete successfully')
    return redirect(url_for('admin_user'))

@app.route('/admin/admin_user_add',methods=['GET','POST'])
def admin_user_add():
    if request.method == 'POST':
        db = get_db()
        if not session.get('username'):
            abort(401)
        db.execute('insert into user (user_name, pass_word) values (?,?)',
                     [request.form['username'], request.form['password']])
        db.commit()
        flash('add user successfully')
        return redirect(url_for('admin_user'))
    return render_template('/admin/admin_user_add.html')

@app.route('/admin/admin_user_edit/<int:id>',methods=['POST','GET'])
def admin_user_edit(id):
    if request.method == 'POST':
        db = get_db()
        if not session.get('username'):
            abort(401)
        db.execute('update user set user_name = ?,pass_word = ? where user_id = ?',
        [request.form['username'],request.form['password'],id])
        db.commit()
        flash('edit user successfully')
        return redirect(url_for('admin_user'))
    db = get_db()
    cur = db.execute('select * from user where user_id = ?',[id])
    data = cur.fetchone()
    return render_template('/admin/admin_user_edit.html',data = data)

@app.errorhandler(404)
def not_found(error):
    #res = make_response(render_template('admin/error.html'),404)
    #res.headers['X-Something'] = 'A value'
    return render_template('/admin/error.html'), 404
    #return res

app.secret_key = '\xc4\xda\xfea\x93@|f(\x9dr\xa2\xb0@%\xb6\x1fF"\xe4\x1a\xa3\xcf'

if __name__ == '__main__':
    app.run(debug=True)
