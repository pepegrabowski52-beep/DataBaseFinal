import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# =============================================================
# WICHTIG: HIER DIE LOGINDATEN FÜR DIE 4 PERSONEN EINTRAGEN
# =============================================================
VALID_USERNAME = "gruppe4"
VALID_PASSWORD = "mein-sicheres-passwort123"


@app.route('/')
def index():
    # Die normale Startseite (Registrierungsformular) für jeden Besucher
    return render_template('index.html')


@app.route('/anmelden', methods=['POST'])
def anmelden():
    # Nimmt die Registrierungsdaten entgegen und speichert sie in der SQLite-Datenbank
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))


@app.route('/benutzer')
def benutzer():
    # --- HIER IST DIE PASSWORT-ABFRAGE (BASIC AUTH) ---
    auth = request.authorization
    
    # Wenn noch keine Daten eingegeben wurden oder sie falsch sind:
    if not auth or auth.username != VALID_USERNAME or auth.password != VALID_PASSWORD:
        # Fordert den Browser auf, das kleine Login-Fenster anzuzeigen
        return ('Bitte anmelden!', 401, {'WWW-Authenticate': 'Basic realm="Login erforderlich"'})
    
    # Wenn die Login-Daten richtig sind, wird die Tabelle geladen:
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    return render_template('benutzer.html', benutzer=user_list)


if __name__ == '__main__':
    # WICHTIG FÜR RAILWAY: host='0.0.0.0' öffnet die App für das Internet.
    # Der Port wird automatisch von Railway zugewiesen.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
