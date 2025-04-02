import sqlite3
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = "monitoring.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ip TEXT NOT NULL,
        status TEXT NOT NULL,
        last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# Register a new service or update existing
def register_service(name, ip):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE name = ?", (name,))
    existing_service = cursor.fetchone()
    
    if existing_service:
        cursor.execute("UPDATE services SET ip = ?, status = 'UP', last_heartbeat = CURRENT_TIMESTAMP WHERE name = ?", (ip, name))
    else:
        cursor.execute("INSERT INTO services (name, ip, status) VALUES (?, ?, 'UP')", (name, ip))
    
    conn.commit()
    conn.close()

# Check service status
def get_services():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    conn.close()
    return services

# Remove stale services
def cleanup_services(timeout=60):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services WHERE (strftime('%s', 'now') - strftime('%s', last_heartbeat)) > ?", (timeout,))
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    ip = data.get('ip')
    if not name or not ip:
        return jsonify({'error': 'Missing service name or IP'}), 400
    
    register_service(name, ip)
    return jsonify({'message': f'Service {name} registered/updated'}), 200

@app.route('/services', methods=['GET'])
def services():
    cleanup_services()
    service_list = get_services()
    return jsonify({'services': service_list})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

