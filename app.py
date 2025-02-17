import sqlite3
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Creazione dell'app Flask
app = Flask(__name__)

# Abilita CORS per tutte le rotte (questo deve venire dopo la creazione dell'app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "API funziona!"})

@app.route('/test')
def test():
    return "Test Route"

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(rule)

# Percorso relativo per il database nella cartella del progetto
db_path = os.path.join(os.getcwd(), 'bookings.db')



# Funzione per connettersi al database SQLite
def get_db_connection():
    conn = sqlite3.connect(db_path)  # Usa il percorso relativo per il database
    conn.row_factory = sqlite3.Row  # Per poter accedere alle colonne come dizionari
    return conn
    

# Funzione per creare la tabella (se non esiste)
def create_table():
    print("Creating the table...")
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

# API per prenotare un tavolo (POST)
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

# API per ottenere tutte le prenotazioni (GET)
@app.route('/api/booking', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    conn.close()

    return jsonify([dict(booking) for booking in bookings]), 200

# API per aggiornare una prenotazione (PUT)
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

# API per cancellare una prenotazione (DELETE)
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
    # Usa la variabile d'ambiente PORT che viene passata da Render
    port = int(os.environ.get("PORT", 5000))  # Usa 5000 come fallback in locale
    app.run(host='0.0.0.0', port=port, debug=True)




