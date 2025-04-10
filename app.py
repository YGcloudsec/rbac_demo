 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = '866439'  

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    sample_users = [
        (1, 'admin_user', 'admin123', 'admin'),
        (2, 'editor_user', 'editor123', 'editor'),
        (3, 'viewer_user', 'viewer123', 'viewer')
    ]
    c.executemany('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)', sample_users)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?', 
                  (username, password))
        user_data = c.fetchone()
        conn.close()
        if user_data:
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for(user.role))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('viewer'))
    return render_template('admin.html')

@app.route('/editor')
@login_required
def editor():
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('viewer'))
    return render_template('editor.html')

@app.route('/viewer')
@login_required
def viewer():
    return render_template('viewer.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
