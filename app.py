from flask import Flask, render_template, request, redirect
import sqlite3
import requests

RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

app = Flask(__name__)

# Create DB table if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)''')
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Get captcha response token
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Verify captcha
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
        return redirect('/success')

    return render_template('signup.html')

@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/users')
def users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email FROM users")
    user_list = c.fetchall()
    conn.close()
    return render_template('users.html', users=user_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)