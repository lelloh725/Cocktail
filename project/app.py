import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le rotte

# Funzione per connettersi al database SQLite
def get_db_connection():
    conn = sqlite3.connect('bookings.db')  # File del database SQLite
    conn.row_factory = sqlite3.Row  # Per poter accedere alle colonne come dizionari
    return conn

# Funzione per creare la tabella (se non esiste)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            people INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Creiamo la tabella all'avvio del server
create_table()

# API per prenotare un tavolo
@app.route('/api/booking', methods=['POST'])
def create_booking():
    data = request.get_json()

    # Verifica se la prenotazione è già presente
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bookings WHERE date = ? AND time = ?', (data['date'], data['time']))
    existing_booking = cursor.fetchone()

    if existing_booking:
        return jsonify({'error': 'Orario già occupato. Scegli un altro orario.'}), 400

    # Inserisce una nuova prenotazione
    cursor.execute('''
        INSERT INTO bookings (name, date, time, people)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['date'], data['time'], data['people']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Prenotazione effettuata con successo!'}), 200

# API per ottenere tutte le prenotazioni
@app.route('/api/booking', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    conn.close()

    return jsonify([dict(booking) for booking in bookings]), 200

# API per aggiornare una prenotazione
@app.route('/api/booking/<int:id>', methods=['PUT'])
def update_booking(id):
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (id,))
    booking = cursor.fetchone()

    if not booking:
        return jsonify({'error': 'Prenotazione non trovata!'}), 404

    # Verifica se il nuovo orario è disponibile
    cursor.execute('SELECT * FROM bookings WHERE date = ? AND time = ?', (data['date'], data['time']))
    existing_booking = cursor.fetchone()

    if existing_booking:
        return jsonify({'error': 'Orario già occupato. Scegli un altro orario.'}), 400

    # Aggiorna la prenotazione
    cursor.execute('''
        UPDATE bookings
        SET time = ?, people = ?
        WHERE id = ?
    ''', (data['time'], data['people'], id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Prenotazione aggiornata con successo!'}), 200

# API per cancellare una prenotazione
@app.route('/api/booking/<int:id>', methods=['DELETE'])
def cancel_booking(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (id,))
    booking = cursor.fetchone()

    if not booking:
        return jsonify({'error': 'Prenotazione non trovata!'}), 404

    # Cancella la prenotazione
    cursor.execute('DELETE FROM bookings WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Prenotazione cancellata con successo!'}), 200

if __name__ == '__main__':
    app.run(debug=True)