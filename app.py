import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Die einzigen 4 erlaubten Konten für die /benutzer Seite
ERLAUBTE_BENUTZER = {
    "mitglied1": "Gruppe4!Sicher2026",
    "mitglied2": "Datenbank?Flask99",
    "mitglied3": "Geheim#Projekt4X",
    "mitglied4": "Railway_Live!77"
}

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
    
    # Prüfen, ob der eingegebene Nutzer existiert UND das Passwort stimmt
    if not auth or auth.username not in ERLAUBTE_BENUTZER or ERLAUBTE_BENUTZER[auth.username] != auth.password:
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
