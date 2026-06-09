import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Erstellt die einfache Datenbank beim Start
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

# 1. Startseite: Lädt deine EINZIGE HTML-Datei (das Register-Formular)
@app.route('/')
def index():
    return render_template('index.html')

# 2. Aktion: Speichert die Daten und schickt den User zurück zum Register
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

# 3. Die /benutzer-Seite: Generiert die Tabelle DIREKT hier im Code,
# ohne dass du eine zweite HTML-Datei auf GitHub brauchst!
@app.route('/benutzer')
def benutzer():
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    # Wir bauen das HTML für die Übersicht direkt als Text im Code zusammen
    html_tabelle = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datenbank Übersicht</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; background: white; }
            th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
            th { background-color: #007bff; color: white; }
        </style>
    </head>
    <body>
        <h2>Registrierte Benutzer in der SQLite-Datenbank:</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Benutzername</th>
                <th>Passwort</th>
            </tr>
    """
    
    # Zeilen für jeden registrierten User hinzufügen
    for user in user_list:
        html_tabelle += f"<tr><td>{user[0]}</td><td>{user[1]}</td><td>{user[2]}</td></tr>"
        
    html_tabelle += """
        </table>
        <br>
        <a href="/">← Zurück zum Register</a>
    </body>
    </html>
    """
    
    return html_tabelle

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
