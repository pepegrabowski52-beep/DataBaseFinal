import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Zugangsdaten für die /benutzer Seite (Das Admin-Login)
VALID_USERNAME = "gruppe4"
VALID_PASSWORD = "mein-sicheres-passwort123"

# Diese Funktion sorgt dafür, dass die Datenbank und die Tabelle 
# automatisch erstellt werden, falls sie auf dem Server fehlen.
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

# 1. HAUPTSEITE (Das Registrierungsformular)
@app.route('/')
def index():
    return render_template('index.html')

# 2. ANMELDE-AKTION (Hier landen die Formulardaten)
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO benutzer (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    # Nach dem Speichern wird der Nutzer wieder auf die Startseite geleitet
    return redirect(url_for('index'))

# 3. BENUTZER-LISTE (Die geheime Admin-Seite)
@app.route('/benutzer')
def benutzer():
    auth = request.authorization
    if not auth or auth.username != VALID_USERNAME or auth.password != VALID_PASSWORD:
        return ('Bitte anmelden!', 401, {'WWW-Authenticate': 'Basic realm="Login erforderlich"'})
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    return render_template('benutzer.html', benutzer=user_list)

# START-BEFEHL (Wichtig für Railway)
if __name__ == '__main__':
    init_db()  # Datenbank prüfen/erstellen
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
