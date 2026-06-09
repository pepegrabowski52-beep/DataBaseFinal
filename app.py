import os
import time
import uuid
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ultratiefes-geheimnis-gruppe-4-2026"

ERLAUBTE_ADMINS = {
    "SniperJohnny": "Gl22ur11",
    "Paul16": "676767",
    "Pepe838": "Knicker",
    "App": "AppLogin"
}

# Verbindung zur permanenten PostgreSQL Datenbank herstellen
def get_db_connection():
    # Railway stellt die DATABASE_URL automatisch bereit
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Tabelle für die User (SERIAL entspricht AUTOINCREMENT)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            passwort TEXT NOT NULL
        )
    ''')
    # Tabelle für die Admin-Sitzungen
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admin_sessions (
            username TEXT PRIMARY KEY,
            session_token TEXT NOT NULL,
            pending_kick INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def check_admin_session():
    if not session.get('admin_logged_in') or not session.get('username') or not session.get('token'):
        return False
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT session_token FROM admin_sessions WHERE username = %s", (session['username'],))
    row = cur.fetchone()
    cur.close()
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
    cur = conn.cursor()
    cur.execute("INSERT INTO benutzer (name, passwort) VALUES (%s, %s)", (benutzername, passwort))
    conn.commit()
    cur.close()
    conn.close()
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erfolgreich</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; text-align: center; padding-top: 100px; background-color: #f0f2f5; color: #333; margin: 0; }
            .box { background: white; padding: 40px; display: inline-block; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); max-width: 450px; }
            h2 { color: #2ecc71; margin-top: 0; font-size: 26px; }
            p { color: #666; font-size: 16px; margin-bottom: 25px; }
            .btn { display: inline-block; padding: 10px 20px; color: white; background: #007bff; text-decoration: none; font-weight: 600; border-radius: 6px; transition: background 0.2s; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .btn-sec { background: #6c757d; }
            .btn-sec:hover { background: #5a6268; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>✔ Registrierung erfolgreich</h2>
            <p>Der Benutzer wurde dauerhaft in der PostgreSQL-Datenbank gespeichert.</p>
            <a class="btn" href="/">Weiterer Benutzer</a>
            <a class="btn btn-sec" href="/geheimer-admin-bereich">Admin-Bereich →</a>
        </div>
    </body>
    </html>
    """

@app.route('/admin-logout')
def logout():
    if session.get('username'):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM admin_sessions WHERE username = %s", (session['username'],))
        conn.commit()
        cur.close()
        conn.close()
    session.clear()
    return redirect('/geheimer-admin-bereich')

@app.route('/admin/delete/<int:user_id>')
def delete_user(user_id):
    if not check_admin_session(): return redirect('/geheimer-admin-bereich')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM benutzer WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(request.referrer or '/geheimer-admin-bereich')

@app.route('/admin/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if not check_admin_session(): return redirect('/geheimer-admin-bereich')
    neuer_name = request.form.get('name')
    neues_pw = request.form.get('passwort')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE benutzer SET name = %s, passwort = %s WHERE id = %s", (neuer_name, neues_pw, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(request.referrer or '/geheimer-admin-bereich')

@app.route('/admin/kick-decision', methods=['POST'])
def kick_decision():
    if not check_admin_session(): return redirect('/geheimer-admin-bereich')
    decision = request.form.get('decision')
    username = session['username']
    
    conn = get_db_connection()
    cur = conn.cursor()
    if decision == 'yes':
        cur.execute("DELETE FROM admin_sessions WHERE username = %s", (username,))
        conn.commit()
        cur.close()
        conn.close()
        session.clear()
        return redirect('/geheimer-admin-bereich')
    else:
        cur.execute("UPDATE admin_sessions SET pending_kick = 0 WHERE username = %s", (username,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(request.referrer or '/geheimer-admin-bereich')

@app.route('/geheimer-admin-bereich', methods=['GET', 'POST'])
def admin_bereich():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ERLAUBTE_ADMINS and ERLAUBTE_ADMINS[username] == password:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=DictCursor)
            cur.execute("SELECT session_token FROM admin_sessions WHERE username = %s", (username,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute("UPDATE admin_sessions SET pending_kick = 1 WHERE username = %s", (username,))
                conn.commit()
                cur.close()
                conn.close()
                return """
                <script>
                    alert("Dieses Konto wird gerade genutzt. Dem angemeldeten Admin wurde eine Anfrage gesendet. Bitte warten Sie kurz und versuchen Sie es gleich erneut.");
                    window.location.href="/geheimer-admin-bereich";
                </script>
                """
            else:
                neues_token = str(uuid.uuid4())
                cur.execute("INSERT INTO admin_sessions (username, session_token, pending_kick) VALUES (%s, %s, 0) ON CONFLICT (username) DO UPDATE SET session_token = EXCLUDED.session_token, pending_kick = 0", (username, neues_token))
                conn.commit()
                cur.close()
                conn.close()
                
                session['admin_logged_in'] = True
                session['username'] = username
                session['token'] = neues_token
                return redirect('/geheimer-admin-bereich')
        else:
            return '<script>alert("Falsche Admin-Daten!"); window.location.href="/geheimer-admin-bereich";</script>'

    if session.get('admin_logged_in') and not check_admin_session():
        session.clear()
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Abgemeldet</title><style>body { font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 100px; background: #f0f2f5; } .box { background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }</style></head>
        <body>
            <div class="box">
                <h3 style="color: #e74c3c;">🔒 Sitzung beendet</h3>
                <p>Sie haben der Übergabe zugestimmt oder die Sitzung wurde überschrieben.</p>
                <a href="/geheimer-admin-bereich" style="color: #007bff; text-decoration: none; font-weight: bold;">Zurück zum Login</a>
            </div>
        </body>
        </html>
        """

    if not session.get('admin_logged_in'):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #74b9ff, #0984e3); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-box { background: white; padding: 40px; border-radius: 14px; box-shadow: 0 12px 30px rgba(0,0,0,0.15); width: 100%; max-width: 350px; text-align: center; }
                h2 { color: #2d3436; margin-bottom: 10px; font-size: 28px; font-weight: 600; }
                p { color: #636e72; font-size: 14px; margin-bottom: 30px; }
                input { width: 100%; padding: 12px 15px; margin: 8px 0; border: 1px solid #dfe6e9; border-radius: 8px; box-sizing: border-box; font-size: 14px; background: #fbfbfb; transition: border 0.2s; }
                input:focus { border-color: #0984e3; outline: none; background: #fff; }
                button { width: 100%; padding: 12px; background: #0984e3; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: background 0.2s; margin-top: 15px; }
                button:hover { background: #000000; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔒 Admin Panel</h2>
                <p>Bitte Logindaten eingeben</p>
                <form method="POST">
                    <input type="text" name="username" placeholder="Admin-Name" required>
                    <input type="password" name="password" placeholder="Passwort" required>
                    <button type="submit">Einloggen</button>
                </form>
            </div>
        </body>
        </html>
        """

    refresh_zeit = request.args.get('refresh', '30')
    username = session['username']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT pending_kick FROM admin_sessions WHERE username = %s", (username,))
    session_row = cur.fetchone()
    
    cur.execute("SELECT * FROM benutzer ORDER BY id ASC")
    user_list = cur.fetchall()
    cur.close()
    conn.close()

    anzeige_kick_popup = ""
    if session_row and session_row['pending_kick'] == 1:
        refresh_zeit = "5"
        anzeige_kick_popup = f"""
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 9999;">
            <div style="background: white; padding: 35px; border-radius: 12px; max-width: 420px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
                <h3 style="color: #e74c3c; margin-top: 0; font-size: 22px;">⚠️ Übernahme-Anfrage</h3>
                <p style="color: #333; font-size: 15px; line-height: 1.5;">Ein weiteres Gerät versucht sich in das Admin-Konto <strong>{username}</strong> einzuloggen.<br><br>Stimmen Sie dem Login zu und melden sich hier ab?</p>
                <form method="POST" action="/admin/kick-decision" style="margin-top: 25px;">
                    <button type="submit" name="decision" value="yes" style="padding: 10px 20px; background: #2ecc71; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-right: 10px;">Ja (Zustimmen & Ausloggen)</button>
                    <button type="submit" name="decision" value="no" style="padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Nein (Ablehnen)</button>
                </form>
            </div>
        </div>
        """

    html_tabelle = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        <meta http-equiv="refresh" content="{refresh_zeit}">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; background-color: #f8f9fa; color: #2d3436; margin: 0; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h2 {{ font-size: 26px; font-weight: 600; color: #2d3436; margin-bottom: 5px; }}
            .user-info {{ color: #74b9ff; font-weight: 600; margin-bottom: 25px; display: inline-block; background: #e3f2fd; padding: 4px 12px; border-radius: 20px; font-size: 13px; }}
            .controls {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; }}
            .control-group {{ display: flex; align-items: center; gap: 8px; }}
            label {{ font-size: 14px; font-weight: 600; color: #636e72; }}
            table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border-radius: 12px; overflow: hidden; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #f1f2f6; }}
            th {{ background-color: #0984e3; color: white; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
            tr:last-child td {{ border-bottom: none; }}
            tr:nth-child(even) {{ background-color: #fbfbfb; }}
            .btn {{ padding: 8px 16px; text-decoration: none; font-weight: 600; border-radius: 6px; font-size: 13px; border: none; cursor: pointer; transition: all 0.2s; }}
            .btn-del {{ background: #ff7675; color: white; }}
            .btn-del:hover {{ background: #e17055; }}
            .btn-save {{ background: #2ecc71; color: white; }}
            .btn-save:hover {{ background: #27ae60; }}
            .btn-logout {{ background: #636e72; color: white; }}
            .btn-logout:hover {{ background: #2d3436; }}
            .inline-form {{ display: flex; gap: 8px; margin: 0; width: 100%; }}
            .inline-form input {{ padding: 8px 12px; border: 1px solid #dfe6e9; border-radius: 6px; font-size: 14px; width: 160px; background: #fbfbfb; transition: border 0.2s; }}
            .inline-form input:focus {{ border-color: #0984e3; background: #fff; outline: none; }}
        </style>
        <script>
            function aendereRefresh() {{
                let sekunden = document.getElementById('refresh-select').value;
                window.location.href = "/geheimer-admin-bereich?refresh=" + sekunden;
            }}
        </script>
    </head>
    <body>
        {anzeige_kick_popup}

        <div class="container">
            <h2>📊 Live-Datenbank Übersicht</h2>
            <span class="user-info">👤 Konto: {username}</span>
            
            <div class="controls">
                <div class="control-group">
                    <label>🔄 Intervall:</label>
                    <input type="number" id="refresh-select" style="width: 70px; padding: 6px; border: 1px solid #dfe6e9; border-radius: 6px;" value="{refresh_zeit}" min="5">
                    <span style="font-size: 14px; color: #636e72; margin-right: 5px;">Sek.</span>
                    <button class="btn btn-save" style="padding: 6px 12px;" onclick="aendereRefresh()">Übernehmen</button>
                </div>
                <a class="btn btn-logout" href="/admin-logout">Ausloggen 🔒</a>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 80px;">ID</th>
                        <th>Benutzername / Passwort bearbeiten</th>
                        <th style="width: 120px; text-align: center;">Aktion</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for user in user_list:
        html_tabelle += f"""
        <tr>
            <td style="font-weight: 600; color: #b2bec3;">#{user['id']}</td>
            <td>
                <form class="inline-form" method="POST" action="/admin/edit/{user['id']}">
                    <input type="text" name="name" value="{user['name']}" required>
                    <input type="text" name="passwort" value="{user['passwort']}" required>
                    <button type="submit" class="btn btn-save">💾 Speichern</button>
                </form>
            </td>
            <td style="text-align: center;">
                <a class="btn btn-del" href="/admin/delete/{user['id']}" onclick="return confirm('Möchten Sie diesen Benutzer wirklich permanent löschen?')">❌ Löschen</a>
            </td>
        </tr>
        """
        
    if not user_list:
        html_tabelle += "<tr><td colspan='3' style='text-align:center; color: #95a5a6; padding: 30px;'>Noch keine Benutzer registriert.</td></tr>"
        
    html_tabelle += """
                </tbody>
            </table>
            <br>
            <a href="/" style="color: #0984e3; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block; margin-top: 10px;">← Zum Registrierungs-Formular</a>
        </div>
    </body>
    </html>
    """
    return html_tabelle

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
