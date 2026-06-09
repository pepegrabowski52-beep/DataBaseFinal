import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Erstellt die einfache Datenbank für deine User
def init_db():
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            passwort TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 1. Startseite mit dem Registrierungsformular
@app.route('/')
def index():
    return render_template('index.html')

# 2. Hier landen die Formulardaten und werden in die DB gespeichert
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    # Nach dem Speichern wird man wieder zur Startseite geleitet
    return redirect(url_for('index'))

# 3. Die Übersichtsseite, die man direkt über /benutzer aufruft
@app.route('/benutzer')
def benutzer():
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    # Schickt die Daten an die benutzer.html
    return render_template('benutzer.html', benutzer=user_list)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
