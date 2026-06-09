import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
# Der Secret Key sorgt dafür, dass die Sitzung (Session) sicher verschlüsselt wird
app.secret_key = "super-geheimes-gruppen-projekt-2026"

DB_PATH = '/tmp/datenbank.db'

# Eure 4 Admin-Konten
ERLAUBTE_ADMINS = {
    "mitglied1": "Gruppe4!Sicher2026",
    "mitglied2": "Datenbank?Flask99",
    "mitglied3": "Geheim#Projekt4X",
    "mitglied4": "Railway_Live!77"
}

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

# 2. Aktion nach dem Registrieren
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Erfolgreich</title><style>body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f9; } .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); } a { color: #007bff; text-decoration: none; font-weight: bold; }</style></head>
    <body>
        <div class="box">
            <h2 style="color: #28a745;">✔ Registrierung erfolgreich!</h2>
            <br>
            <a href="/">← Weiteren Benutzer registrieren</a> | <a href="/benutzer">Zur Admin-Datenbank →</a>
        </div>
    </body>
    </html>
    """

# 3. Die /benutzer-Seite: Prüft, ob man in DIESEM Moment angemeldet ist
@app.route('/benutzer', methods=['GET', 'POST'])
def benutzer():
    # Wenn der Admin das Login-Formular abschickt:
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[username] == password:
            session['eingeloggt'] = True  # Erlaube Zugriff für diesen Klick
        else:
            return '''
            <script>alert("Falsche Admin-Daten!"); window.location.href="/benutzer";</script>
            '''

    # WICHTIG: Wenn man nicht frisch eingeloggt ist, zeige die Login-Maske
    if not session.get('eingeloggt'):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 320px; text-align: center; }
                input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>Admin Login</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Admin-Nutzername" required>
                    <input type="password" name="password" placeholder="Passwort" required>
                    <button type="submit">Daten ansehen</button>
                </form>
                <br>
                <a href="/" style="color: #666; font-size: 14px; text-decoration: none;">← Zum Register</a>
            </div>
        </body>
        </html>
        """

    # --- AB HIER: Der Admin ist eingeloggt und sieht die Tabelle ---
    
    # TRICK: Wir zerstören die Session SOFORT wieder für den nächsten Aufruf!
    # Dadurch muss man sich beim nächsten Mal oder beim Aktualisieren IMMER neu anmelden.
    session['eingeloggt'] = False 

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
        <style>
            body { font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }
            table { border-collapse: collapse; width: 100%; max-width: 600px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f8f9fa; }
            .warnung { color: #d9534f; font-weight: bold; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h2>Übersicht der SQLite-Datenbank:</h2>
        <p class="warnung">🔒 Einmalige Ansicht: Wenn du die Seite aktualisierst, musst du dich neu anmelden!</p>
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
