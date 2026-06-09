import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "super-geheimes-gruppen-geheimnis" # Wichtig für Sessions

# Diese Funktion erstellt BEIDE Tabellen automatisch beim Start
def init_db():
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    
    # Tabelle 1: Für die Leute, die sich auf der Startseite registrieren
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrierte_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            passwort TEXT NOT NULL
        )
    ''')
    
    # Tabelle 2: Für die 4 Admins, die die Liste sehen dürfen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_konten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            passwort TEXT NOT NULL
        )
    ''')
    
    # Die 4 Admin-Konten in die Datenbank einfügen (falls sie noch nicht existieren)
    admins = [
        ("mitglied1", "Gruppe4!Sicher2026"),
        ("mitglied2", "Datenbank?Flask99"),
        ("mitglied3", "Geheim#Projekt4X"),
        ("mitglied4", "Railway_Live!77")
    ]
    for name, pw in admins:
        try:
            cursor.execute("INSERT INTO admin_konten (name, passwort) VALUES (?, ?)", (name, pw))
        except sqlite3.IntegrityError:
            pass # Wenn der Admin schon drin ist, einfach überspringen
            
    conn.commit()
    conn.close()

# 1. STARTSEITE: Normales Registrierungsformular für User
@app.route('/')
def index():
    return render_template('index.html')

# Aktion für die Startseite: Speichert User in "registrierte_user"
@app.route('/anmelden', methods=['POST'])
def anmelden():
    benutzername = request.form['benutzername']
    passwort = request.form['passwort']
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registrierte_user (name, passwort) VALUES (?, ?)", (benutzername, passwort))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# 2. ADMIN-LOGIN-SEITE: Hier landen Admins, wenn sie auf /benutzer wollen
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('datenbank.db')
        cursor = conn.cursor()
        # Prüfen, ob Admin in der Tabelle "admin_konten" existiert
        cursor.execute("SELECT * FROM admin_konten WHERE name = ? AND passwort = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            session['admin_eingeloggt'] = True
            return redirect(url_for('benutzer'))
        else:
            flash("Falscher Admin-Name oder Passwort!")
            
    return render_template('admin_login.html')

# 3. DIE GEHEIME DATENBANK-ANSICHT (Zeigt alle registrierten User)
@app.route('/benutzer')
def benutzer():
    # Wenn der Admin nicht eingeloggt ist, schicke ihn zum Login-Formular
    if not session.get('admin_eingeloggt'):
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('datenbank.db')
    cursor = conn.cursor()
    # Holt alle User aus der ersten Tabelle
    cursor.execute("SELECT * FROM registrierte_user")
    user_list = cursor.fetchall()
    conn.close()
    
    return render_template('benutzer.html', benutzer=user_list)

# LOGOUT für den Admin
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_eingeloggt', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
