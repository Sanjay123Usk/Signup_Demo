from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import requests

app = Flask(__name__)

RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
app.secret_key = 'SanjayKumar@12345'


@app.route('/')
def home():
    return render_template('home.html')

# Create DB table if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)''')
    conn.commit()
    conn.close()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        recaptcha_response = request.form.get('g-recaptcha-response')

        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        captcha_res = requests.post(verify_url, data=payload).json()

        if not captcha_res.get('success'):
            return "Captcha verification failed. Please try again."

        # Save to database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                  (name, email, password))
        conn.commit()
        conn.close()
        return redirect('/starter_page')

    return render_template('signup.html')

@app.route('/starter_page')
def starter_page():
    return render_template('starter_page.html')


@app.route('/users')
def users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email FROM users")
    user_list = c.fetchall()
    conn.close()
    return render_template('users.html', users=user_list)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect('/starter_page')
        else:
            flash('Invalid email or password')
            return redirect('/login')

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome, {session['user_name']}! <a href='/logout'>Logout</a>"
    else:
        return redirect('/login')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/routes')
def show_routes():
    return '<br>'.join(sorted(rule.rule for rule in app.url_map.iter_rules()))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)