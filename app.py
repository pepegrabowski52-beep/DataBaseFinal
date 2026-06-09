import os
import sqlite3
import time
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
# Der Secret Key sorgt dafür, dass sich der Browser merkt, dass du eingeloggt bist!
app.secret_key = "geheim-projekt-gruppe-4-2026"

# Sicherer Pfad im /tmp/ Ordner für echte Live-Updates ohne Sperren
DB_PATH = '/tmp/datenbank_live.db'

# Eure 4 erlaubten Admin-Konten
ERLAUBTE_ADMINS = {
    "SniperJohnny": "Gl22ur11",
    "Paul16": "676767",
    "Pepe838": "Knicker",
    "App": "AppLogin"
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
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
            <h2 style="color: #28a745;">✔ Benutzer wurde erstellt!</h2>
            <p>Der Eintrag wurde live in die Datenbank geschrieben.</p>
            <br>
            <a href="/">← Weiteren Benutzer registrieren</a> | <a href="/geheimer-admin-bereich">Zum Admin-Bereich →</a>
        </div>
    </body>
    </html>
    """

# Route zum Abmelden, falls man sich aktiv ausloggen will
@app.route('/admin-logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 3. GEHEIMER PFAD: Passwort-Abfrage + Einmaliges Einloggen + Live-Tabelle
@app.route('/geheimer-admin-bereich', methods=['GET', 'POST'])
def admin_bereich():
    # Wenn der Admin das Passwort-Formular abschickt:
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[username] == password:
            session['admin_logged_in'] = True  # Setzt das "Merker"-Flag für den Browser
            return redirect('/geheimer-admin-bereich')
        else:
            return '''
            <script>alert("Zugriff verweigert! Falsche Admin-Daten."); window.location.href="/geheimer-admin-bereich";</script>
            '''

    # WICHTIG: Wenn man NICHT eingeloggt ist, zeige die Passwort-Maske
    if not session.get('admin_logged_in'):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sicherheitsbereich</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 320px; text-align: center; }
                input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔒 Admin Login</h2>
                <p style="color: #666; font-size: 14px;">Bitte verifizieren Sie sich für die Live-Datenbank.</p>
                <form method="POST">
                    <input type="text" name="username" placeholder="Admin-Name" required>
                    <input type="password" name="password" placeholder="Passwort" required>
                    <button type="submit">Einloggen</button>
                </form>
            </div>
        </body>
        </html>
        """

    # --- AB HIER: Du bist eingeloggt! (Die Session bleibt aktiv!) ---
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    html_tabelle = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live-Datenbank</title>
        <meta http-equiv="refresh" content="2"> <style>
            body { font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .info { color: #28a745; font-weight: bold; margin-bottom: 15px; }
            .btn { color: #d9534f; text-decoration: none; font-weight: bold; margin-left: 20px; }
        </style>
    </head>
    <body>
        <h2>Live-Übersicht der registrierten Benutzer:</h2>
        <p class="info">🔄 Verbindung aktiv. Neue Einträge erscheinen alle 2 Sekunden automatisch.</p>
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
        html_tabelle += "<tr><td colspan='3' style='text-align:center;'>Noch keine Benutzer registriert. Datenkanal läuft!</td></tr>"
        
    html_tabelle += """
        </table>
        <br>
        <a href="/" style="color: #007bff; text-decoration: none; font-weight: bold;">← Zum Register</a>
        <a class="btn" href="/admin-logout">Ausloggen 🔒</a>
    </body>
    </html>
    """
    return html_tabelle

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
