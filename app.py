import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = 'datenbank.db'

def get_db_connection():
    # Extrem hoher Timeout (60 Sekunden) und sofortiges Schreiben, damit Railway nicht blockiert
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db_connection()
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

# 1. Startseite: Lädt dein Register-Formular
@app.route('/')
def index():
    return render_template('index.html')

# 2. Aktion nach dem Registrieren
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    # Leitet den User nach dem Registrieren sofort wieder auf das leere Register-Formular um
    return redirect(url_for('index'))

# 3. Die /benutzer-Seite: Komplett OFFEN, lädt sich alle 2 Sekunden von selbst neu
@app.route('/benutzer')
def benutzer():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    html_tabelle = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datenbank Übersicht</title>
        <meta http-equiv="refresh" content="2"> <style>
            body { font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .info-text { color: #28a745; font-weight: bold; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h2>Einfache SQLite-Datenbank Übersicht:</h2>
        <p class="info-text">🔄 Diese Seite aktualisiert sich alle 2 Sekunden von selbst.</p>
        <table>
            <tr>
                <th>ID</th>
                <th>Benutzername</th>
                <th>Passwort</th>
            </tr>
    """
    
    for user in user_list:
        html_tabelle += f"<tr><td>{user[0]}</td><td>{user[1]}</td><td>{user[2]}</td></tr>"
        
    if not user_list:
        html_tabelle += "<tr><td colspan='3' style='text-align:center;'>Noch keine Daten vorhanden.</td></tr>"
        
    html_tabelle += """
        </table>
        <br>
        <a href="/" style="color: #007bff; text-decoration: none; font-weight: bold;">← Zurück zum Register</a>
    </body>
    </html>
    """
    return html_tabelle

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
