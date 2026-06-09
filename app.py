from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'datenbank.db'

# 1. Lädt die index.html aus dem 'templates' Ordner
@app.route('/')
def home():
    return render_template('index.html')

# 2. Verarbeitet die Daten aus dem Formular
@app.route('/register', methods=['POST'])
def register():
    name = request.form['benutzername']
    email = request.form['email']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (benutzername, email, passwort) VALUES (?, ?, ?);", (name, email, passwort))
    conn.commit()
    conn.close()
    
    return f"<h1>Erfolg!</h1><p>Benutzer {name} wurde gespeichert!</p><a href='/benutzer'>Hier alle Benutzer ansehen</a>"

# 3. Zeigt alle Benutzer als JSON an
@app.route('/benutzer', methods=['GET'])
def get_benutzer():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, benutzername, email, registriert_am FROM benutzer;")
    users = cursor.fetchall()
    conn.close()
    
    user_list = [{"id": u[0], "benutzername": u[1], "email": u[2], "registriert_am": u[3]} for u in users]
    return jsonify(user_list)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)