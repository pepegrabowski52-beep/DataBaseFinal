import os
import sqlite3
import time
import uuid
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ultratiefes-geheimnis-gruppe-4-2026"

DB_PATH = '/tmp/datenbank_live.db'

ERLAUBTE_ADMINS = {
    "SniperJohnny": "Gl22ur11",
    "Paul16": "676767",
    "Pepe838": "Knicker",
    "App": "AppLogin"
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Tabelle für die User
    conn.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            passwort TEXT NOT NULL
        )
    ''')
    # Tabelle für die Admin-Sitzungen (wichtig für den Single-Login)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admin_sessions (
            username TEXT PRIMARY KEY,
            session_token TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Hilfsfunktion: Prüft, ob der Admin noch das aktuelle Token besitzt
def check_admin_session():
    if not session.get('admin_logged_in') or not session.get('username') or not session.get('token'):
        return False
    conn = get_db_connection()
    row = conn.execute("SELECT session_token FROM admin_sessions WHERE username = ?", (session['username'],)).fetchone()
    conn.close()
    if row and row['session_token'] == session['token']:
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    conn = get_db_connection()
    conn.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Erfolgreich</title><style>body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f9; } .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); } a { color: #007bff; text-decoration: none; font-weight: bold; }</style></head>
    <body>
        <div class="box">
            <h2 style="color: #28a745;">✔ Benutzer wurde erstellt!</h2>
            <br><a href="/">← Weiteren Benutzer registrieren</a> | <a href="/geheimer-admin-bereich">Zum Admin-Bereich →</a>
        </div>
    </body>
    </html>
    """

@app.route('/admin-logout')
def logout():
    session.clear()
    return redirect('/geheimer-admin-bereich')

# ---------------- ADMIN FUNKTIONEN (LÖSCHEN & BEARBEITEN) ----------------

@app.route('/admin/delete/<int:user_id>')
def delete_user(user_id):
    if not check_admin_session(): return redirect('/geheimer-admin-bereich')
    conn = get_db_connection()
    conn.execute("DELETE FROM benutzer WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/geheimer-admin-bereich')

@app.route('/admin/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if not check_admin_session(): return redirect('/geheimer-admin-bereich')
    neuer_name = request.form.get('name')
    neues_pw = request.form.get('passwort')
    conn = get_db_connection()
    conn.execute("UPDATE benutzer SET name = ?, passwort = ? WHERE id = ?", (neuer_name, neues_pw, user_id))
    conn.commit()
    conn.close()
    return redirect('/geheimer-admin-bereich')

# ---------------- GEHEIMER ADMIN BEREICH ----------------

@app.route('/geheimer-admin-bereich', methods=['GET', 'POST'])
def admin_bereich():
    if request.method == 'POST':
        # Fall 1: Normaler Login-Versuch
        if 'login_attempt' in request.form:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[username] == password:
                conn = get_db_connection()
                existing = conn.execute("SELECT session_token FROM admin_sessions WHERE username = ?", (username,)).fetchone()
                conn.close()
                
                if existing:
                    # Konflikt! Jemand ist bereits mit diesen Daten drin. Zeige die Zustimmen/Ablehnen Box:
                    return f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Konflikt</title><style>body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }} .box {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }} button {{ padding: 10px 20px; margin: 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }} .yes {{ background: #dc3545; color: white; }} .no {{ background: #6c757d; color: white; }}</style></head>
                    <body>
                        <div class="box">
                            <h2>⚠️ Konto bereits aktiv!</h2>
                            <p>Ein anderer Admin ist gerade mit dem Konto <strong>{username}</strong> angemeldet.</p>
                            <p>Möchten Sie den anderen Admin ausloggen und die Sitzung übernehmen?</p>
                            <form method="POST">
                                <input type="hidden" name="username" value="{username}">
                                <button type="submit" name="kick_decision" value="yes" class="yes">Ja (Zustimmen & Einloggen)</button>
                                <button type="submit" name="kick_decision" value="no" class="no">Nein (Ablehnen)</button>
                            </form>
                        </div>
                    </body>
                    </html>
                    """
                else:
                    # Kein Konflikt -> Direkt einloggen
                    neues_token = str(uuid.uuid4())
                    conn = get_db_connection()
                    conn.execute("INSERT INTO admin_sessions (username, session_token) VALUES (?, ?)", (username, neues_token))
                    conn.commit()
                    conn.close()
                    
                    session['admin_logged_in'] = True
                    session['username'] = username
                    session['token'] = neues_token
                    return redirect('/geheimer-admin-bereich')
            else:
                return '<script>alert("Falsche Admin-Daten!"); window.location.href="/geheimer-admin-bereich";</script>'

        # Fall 2: Entscheidung nach der Kick-Abfrage
        elif 'kick_decision' in request.form:
            decision = request.form.get('kick_decision')
            username = request.form.get('username')
            
            if decision == 'yes':
                neues_token = str(uuid.uuid4())
                conn = get_db_connection()
                # Überschreibe das Token in der DB -> Der alte Admin fliegt raus!
                conn.execute("UPDATE admin_sessions SET session_token = ? WHERE username = ?", (neues_token, username))
                conn.commit()
                conn.close()
                
                session['admin_logged_in'] = True
                session['username'] = username
                session['token'] = neues_token
                return redirect('/geheimer-admin-bereich')
            else:
                return redirect('/geheimer-admin-bereich')

    # PRÜFUNG: Wenn man eingeloggt war, aber jemand anderes hat einen gekickt (Zustimmen geklickt):
    if session.get('admin_logged_in') and not check_admin_session():
        session.clear()
        return '<script>alert("Sie wurden abgemeldet, da sich ein anderer Admin mit diesen Daten eingeloggt hat!"); window.location.href="/geheimer-admin-bereich";</script>'

    # Wenn nicht eingeloggt, zeige die Login-Maske
    if not session.get('admin_logged_in'):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login</title>
            <style>body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; } .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 320px; text-align: center; } input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; } button { width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }</style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔒 Admin Login</h2>
                <form method="POST">
                    <input type="hidden" name="login_attempt" value="1">
                    <input type="text" name="username" placeholder="Admin-Name" required>
                    <input type="password" name="password" placeholder="Passwort" required>
                    <button type="submit">Einloggen</button>
                </form>
            </div>
        </body>
        </html>
        """

    # --- AB HIER: Erfolgreich drin! ---
    # Refresh-Zeit ermitteln (Standard: 30 Sekunden, falls nichts im Browser gespeichert ist)
    refresh_zeit = request.args.get('refresh', '30')

    conn = get_db_connection()
    user_list = conn.execute("SELECT * FROM benutzer").fetchall()
    conn.close()
    
    html_tabelle = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live-Datenbank</title>
        <meta http-equiv="refresh" content="{refresh_zeit}">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f9; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 850px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 15px; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #007bff; color: white; }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            .controls {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); max-width: 820px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }}
            .btn {{ padding: 6px 12px; text-decoration: none; font-weight: bold; border-radius: 4px; font-size: 14px; border: none; cursor: pointer; }}
            .btn-del {{ background: #dc3545; color: white; }}
            .btn-save {{ background: #28a745; color: white; }}
            .btn-logout {{ background: #6c757d; color: white; }}
            .inline-form {{ display: flex; gap: 5px; margin: 0; }}
            .inline-input {{ padding: 4px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }}
        </style>
        <script>
            function aendereRefresh() {{
                let sekunden = document.getElementById('refresh-select').value;
                window.location.href = "/geheimer-admin-bereich?refresh=" + sekunden;
            }}
        </script>
    </head>
    <body>
        <h2>Live-Übersicht (Eingeloggt als: {session['username']}):</h2>
        
        <div class="controls">
            <div>
                <label style="font-weight: bold;">🔄 Aktualisierungs-Intervall: </label>
                <input type="number" id="refresh-select" class="inline-input" style="width: 60px;" value="{refresh_zeit}" min="5"> Sekunden
                <button class="btn btn-save" style="padding: 4px 8px;" onclick="aendereRefresh()">Übernehmen</button>
            </div>
            <a class="btn btn-logout" href="/admin-logout">Ausloggen 🔒</a>
        </div>

        <table>
            <tr>
                <th>ID</th>
                <th>Benutzername / Passwort bearbeiten</th>
                <th>Aktion</th>
            </tr>
    """
    
    for user in user_list:
        html_tabelle += f"""
        <tr>
            <td>{user['id']}</td>
            <td>
                <form class="inline-form" method="POST" action="/admin/edit/{user['id']}">
                    <input type="text" name="name" class="inline-input" value="{user['name']}" required>
                    <input type="text" name="passwort" class="inline-input" value="{user['passwort']}" required>
                    <button type="submit" class="btn btn-save">💾 Speichern</button>
                </form>
            </td>
            <td>
                <a class="btn btn-del" href="/admin/delete/{user['id']}" onclick="return confirm('Sicher löschen?')">❌ Löschen</a>
            </td>
        </tr>
        """
        
    if not user_list:
        html_tabelle += "<tr><td colspan='3' style='text-align:center;'>Noch keine Benutzer registriert.</td></tr>"
        
    html_tabelle += """
        </table>
        <br>
        <a href="/" style="color: #007bff; text-decoration: none; font-weight: bold;">← Zum Register-Formular</a>
    </body>
    </html>
    """
    return html_tabelle

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
