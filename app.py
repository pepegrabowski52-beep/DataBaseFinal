import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -------------------------------------------------------------
# HIER DIE ZUGANGSDATEN FÜR DEINE 4 PERSONEN EINTRAGEN
# Ändere "gruppe4" und "mein-sicheres-passwort123" nach Wunsch ab!
# -------------------------------------------------------------
VALID_USERNAME = "gruppe4"
VALID_PASSWORD = "mein-sicheres-passwort123"

@app.route('/')
def index():
    # Zeigt die normale Startseite (Registrierungsformular) an
    return render_template('index.html')

@app.route('/anmelden', methods=['POST'])
def anmelden():
    # Nimmt die Daten aus dem Formular entgegen und speichert sie
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
    # PASSPORT-SCHUTZ: Prüft, ob die Login-Daten eingegeben wurden und stimmen
    auth = request.authorization
    if not auth or auth.username != VALID_USERNAME or auth.password != VALID_PASSWORD:
        # Wenn die Daten falsch sind oder fehlen, poppt das Anmeldefenster im Browser auf
        return ('Bitte anmelden!', 401, {'WWW-Authenticate': 'Basic realm="Login erforderlich"'})
    
    # Wenn die Anmeldung erfolgreich war, wird die Liste aus der Datenbank geladen
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM benutzer")
    user_list = cursor.fetchall()
    conn.close()
    
    return render_template('benutzer.html', benutzer=user_list)

if __name__ == '__main__':
    # Railway-optimierte Starteinstellungen
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
