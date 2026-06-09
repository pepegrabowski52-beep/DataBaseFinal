import os
import sqlite3
import uuid
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "ultratiefes-geheimnis-gruppe-4-2026"

# Absoluter Pfad für die Datenbank-Datei
DB_PATH = os.path.join(os.getcwd(), 'datenbank.db')

ERLAUBTE_ADMINS = {
    "SniperJohnny": "Gl22ur11",
    "Paul16": "676767",
    "Pepe838": "Knicker",
    "App": "AppLogin"
}

def get_db_connection():
    # check_same_thread=False verhindert den "Internal Server Error"
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS benutzer (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, passwort TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS admin_sessions (username TEXT PRIMARY KEY, session_token TEXT NOT NULL, pending_kick INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anmelden', methods=['POST'])
def anmelden():
    name = request.form['benutzername']
    pw = request.form['passwort']
    conn = get_db_connection()
    conn.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (name, pw))
    conn.commit()
    conn.close()
    return '<html><body style="font-family:sans-serif; text-align:center; padding-top:50px;"><h2>✔ Erfolgreich registriert!</h2><a href="/">Zurück</a></body></html>'

@app.route('/geheimer-admin-bereich', methods=['GET', 'POST'])
def admin_bereich():
    if request.method == 'POST':
        user, pw = request.form.get('username'), request.form.get('password')
        if user in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[user] == pw:
            conn = get_db_connection()
            if conn.execute("SELECT * FROM admin_sessions WHERE username = ?", (user,)).fetchone():
                conn.execute("UPDATE admin_sessions SET pending_kick = 1 WHERE username = ?", (user,))
                conn.commit(); conn.close()
                return '<script>alert("Konto aktiv. Anfrage gesendet."); window.location.href="/geheimer-admin-bereich";</script>'
            token = str(uuid.uuid4())
            conn.execute("INSERT INTO admin_sessions (username, session_token) VALUES (?, ?)", (user, token))
            conn.commit(); conn.close()
            session.update({'admin': True, 'user': user, 'token': token})
            return redirect('/geheimer-admin-bereich')
        return '<script>alert("Falsche Daten!"); window.location.href="/geheimer-admin-bereich";</script>'
    
    if not session.get('admin'):
        return '''<body style="background:#0984e3; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; font-family:sans-serif;">
        <form method="POST" style="background:white; padding:40px; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.2);">
        <h2 style="margin-top:0;">🔒 Admin Login</h2>
        <input name="username" placeholder="Name" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <input type="password" name="password" placeholder="Passwort" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <button type="submit" style="width:100%; padding:10px; background:#0984e3; color:white; border:none; cursor:pointer;">Login</button></form></body>'''

    conn = get_db_connection()
    user_list = conn.execute("SELECT * FROM benutzer").fetchall()
    session_data = conn.execute("SELECT pending_kick FROM admin_sessions WHERE username = ?", (session['user'],)).fetchone()
    conn.close()

    popup = ""
    if session_data and session_data['pending_kick'] == 1:
        popup = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); display:flex; justify-content:center; align-items:center;">' \
                '<div style="background:white; padding:20px; border-radius:8px;"><h3>Übernahme-Anfrage!</h3>' \
                '<form method="POST" action="/kick-decision"><button name="decision" value="yes">Zustimmen</button>' \
                '<button name="decision" value="no">Ablehnen</button></form></div></div>'

    html = f'<html><body style="padding:40px; font-family:sans-serif;">{popup}<h2>Dashboard: {session["user"]}</h2><a href="/logout">Logout</a>'
    html += '<table width="100%" border="1" style="border-collapse:collapse; margin-top:20px;">'
    for u in user_list:
        html += f'<tr><td>{u["id"]}</td><td>{u["name"]}</td><td>{u["passwort"]}</td><td><a href="/del/{u["id"]}">Löschen</a></td></tr>'
    return html + '</table></body></html>'

@app.route('/kick-decision', methods=['POST'])
def kick_decision():
    conn = get_db_connection()
    if request.form.get('decision') == 'yes':
        conn.execute("DELETE FROM admin_sessions WHERE username = ?", (session.get('user'),))
        conn.commit(); conn.close()
        session.clear()
    else:
        conn.execute("UPDATE admin_sessions SET pending_kick = 0 WHERE username = ?", (session.get('user'),))
        conn.commit(); conn.close()
    return redirect('/geheimer-admin-bereich')

@app.route('/del/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM benutzer WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect('/geheimer-admin-bereich')

@app.route('/logout')
def logout():
    conn = get_db_connection()
    conn.execute("DELETE FROM admin_sessions WHERE username = ?", (session.get('user'),))
    conn.commit(); conn.close()
    session.clear()
    return redirect('/geheimer-admin-bereich')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
