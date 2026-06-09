import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "super-geheimes-gruppen-projekt-2026"

DB_PATH = 'datenbank.db'

# Eure 4 Admin-Konten
ERLAUBTE_ADMINS = {
    "SniperJohnny": "Gl22ur11",
    "Paul16": "676767",
    "Pepe838": "Knicker",
    "App": "AppLogin"
}

# Hilfsfunktion, um eine sichere Verbindung zur DB aufzubauen (verhindert Sperren)
def get_db_connection():
    # timeout=20 zwingt den Server, bis zu 20 Sekunden zu warten, falls die DB gerade blockiert ist
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    # Aktiviert den WAL-Modus für echtes gleichzeitiges Schreiben und Lesen
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
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
    
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")
    
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Erfolgreich</title><style>body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f9; } .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); } a { color: #007bff; text-decoration: none; font-weight: bold; }</style></head>
    <body>
        <div class="box">
            <h2 style="color: #28a745;">✔ Registrierung erfolgreich!</h2>
            <p>Die Daten wurden dauerhaft und live in die SQLite-Datenbank übertragen.</p>
            <br>
            <a href="/">← Weiteren Benutzer registrieren</a> | <a href="/benutzer">Zur Admin-Datenbank →</a>
        </div>
    </body>
    </html>
    """

# Geheimer Hintergrund-Kanal für die JavaScript-Live-Daten
@app.route('/api/live-daten')
def live_daten():
    if not session.get('eingeloggt'):
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM benutzer")
    rows = cursor.fetchall()
    conn.close()
    
    # Daten für JavaScript lesbar machen
    user_list = [ [row['id'], row['name'], row['passwort']] for row in rows ]
    return jsonify(user_list)

# Route zum Abmelden
@app.route('/logout')
def logout():
    session.pop('eingeloggt', None)
    return redirect(url_for('index'))

# 3. Die /benutzer-Seite mit geschütztem Login und JavaScript-Live-Refresh
@app.route('/benutzer', methods=['GET', 'POST'])
def benutzer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[username] == password:
            session['eingeloggt'] = True  
        else:
            return '''
            <script>alert("Falsche Admin-Daten!"); window.location.href="/benutzer";</script>
            '''

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

    return """
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
            .info-text { color: #28a745; font-weight: bold; margin-bottom: 15px; }
            .btn { color: #007bff; text-decoration: none; font-weight: bold; margin-right: 20px; }
            .logout { color: #dc3545; }
        </style>
        <script>
            async function ladeDatenLive() {
                try {
                    let response = await fetch('/api/live-daten');
                    let userList = await response.json();
                    let tabelleBody = document.getElementById('user-table-body');
                    
                    if (userList.length === 0) {
                        tabelleBody.innerHTML = "<tr><td colspan='3' style='text-align:center;'>Noch keine Daten vorhanden.</td></tr>";
                        return;
                    }
                    
                    let html = "";
                    userList.forEach(user => {
                        html += `<tr><td>${user[0]}</td><td>${user[1]}</td><td>${user[2]}</td></tr>`;
                    });
                    tabelleBody.innerHTML = html;
                } catch (e) {
                    console.log("Fehler beim Live-Laden", e);
                }
            }
            
            setInterval(ladeDatenLive, 3000);
            window.onload = ladeDatenLive;
        </script>
    </head>
    <body>
        <h2>Übersicht der SQLite-Datenbank (Echte Live-Anzeige):</h2>
        <p class="info-text">🔒 Angemeldet als Admin. Neue User ploppen hier sofort automatisch auf.</p>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Benutzername</th>
                    <th>Passwort</th>
                </tr>
            </thead>
            <tbody id="user-table-body">
                </tbody>
        </table>
        <br>
        <a class="btn" href="/">← Zurück zum Register</a>
        <a class="btn logout" href="/logout">Abmelden 🔒</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
