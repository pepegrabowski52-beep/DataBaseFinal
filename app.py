import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

VALID_USERNAME = "gruppe4"
VALID_PASSWORD = "mein-sicheres-passwort123"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/benutzer')
def benutzer():
    auth = request.authorization
    if not auth or auth.username != VALID_USERNAME or auth.password != VALID_PASSWORD:
        return ('Bitte anmelden!', 401, {'WWW-Authenticate': 'Basic realm="Login erforderlich"'})
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    return render_template('benutzer.html', benutzer=user_list)

if __name__ == '__main__':
    # Dieser Block ist absolut Pflicht für Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

