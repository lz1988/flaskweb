#encoding:utf-8
import os
import sqlite3
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

#@app.cli.command('initdb')
#def initdb_command():
    """Creates the database tables."""
    #init_db()
    #print('Initialized the database.')


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
    cur = db.execute('select title, text, firstcreate from entries order by id desc')
    entries = cur.fetchall()
    return render_template('home.html', entries=entries)

@app.route('/detail/<int:id>')
def detail(id):
    return 'id : %d' % id

@app.route('/view/<username>')
def view(username):
    return 'user %s' % username

@app.route('/contact')
def contact():
    return 'contact';

@app.route('/about/')
def about():
    return 'about';

@app.route('/nihao/')
@app.route('/nihao/<name>')
def nihao(name=None):
    return render_template('nihao.html', name=name)

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were Logged out')
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    #g.db = connect_db()
    db = get_db()
    if not session.get('username'):
        abort(401)
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

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

@app.errorhandler(404)
def not_found(error):
    res = make_response(render_template('error.html'),404)
    res.headers['X-Something'] = 'A value'
    return res

app.secret_key = '\xc4\xda\xfea\x93@|f(\x9dr\xa2\xb0@%\xb6\x1fF"\xe4\x1a\xa3\xcf'

if __name__ == '__main__':
    app.run(debug=True)
