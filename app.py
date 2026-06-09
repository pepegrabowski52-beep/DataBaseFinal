import os
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# WICHTIG FÜR RAILWAY: Wir legen die Datenbank in den beschreibbaren /tmp/ Ordner,
# damit die Einträge LIVE gespeichert und sofort angezeigt werden!
DB_PATH = '/tmp/datenbank.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

# 2. Aktion nach dem Registrieren: Kein "Nicht gefunden" mehr!
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    # Statt fehlerhafter Weiterleitung zeigen wir direkt eine Erfolgsseite an
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erfolgreich</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f9; }
            .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            a { color: #007bff; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2 style="color: #28a745;">✔ Registrierung erfolgreich!</h2>
            <p>Der Benutzer wurde live in die SQLite-Datenbank eingetragen.</p>
            <br>
            <a href="/">← Weiteren Benutzer registrieren</a> | <a href="/benutzer">Zur Datenbank-Übersicht →</a>
        </div>
    </body>
    </html>
    """

# 3. Die /benutzer-Seite: Komplett ohne Passwort und lädt die Daten LIVE aus /tmp/
@app.route('/benutzer')
def benutzer():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    html_tabelle = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datenbank Übersicht</title>
        <meta http-equiv="refresh" content="5"> <style>
            body { font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .info { color: #666; font-size: 14px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h2>Live-Übersicht der SQLite-Datenbank:</h2>
        <p class="info">🔄 Diese Seite aktualisiert sich alle 5 Sekunden automatisch live.</p>
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
