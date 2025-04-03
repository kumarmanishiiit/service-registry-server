import sqlite3
import time
from flask import Flask, request, jsonify, render_template
from datetime import datetime

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
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("SELECT * FROM services WHERE name = ?", (name,))
    existing_service = cursor.fetchone()
    
    if existing_service:
        cursor.execute("UPDATE services SET ip = ?, status = 'UP', last_heartbeat = ? WHERE name = ?", 
                      (ip, current_time, name))
    else:
        cursor.execute("INSERT INTO services (name, ip, status, last_heartbeat) VALUES (?, ?, 'UP', ?)", 
                      (name, ip, current_time))
    
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

@app.route('/')
def index():
    cleanup_services()
    services = get_services()
    # Convert services to a more UI-friendly format
    formatted_services = []
    for service in services:
        try:
            # Handle datetime with microseconds
            last_heartbeat_str = service[4]
            if '.' in last_heartbeat_str:
                last_heartbeat = datetime.strptime(last_heartbeat_str, '%Y-%m-%d %H:%M:%S.%f')
            else:
                last_heartbeat = datetime.strptime(last_heartbeat_str, '%Y-%m-%d %H:%M:%S')
            
            current_time = datetime.now()
            time_diff = (current_time - last_heartbeat).total_seconds()
            status = 'UP' if time_diff < 60 else 'DOWN'
            
            formatted_services.append({
                'id': service[0],
                'name': service[1],
                'ip': service[2],
                'status': status,
                'last_heartbeat': last_heartbeat_str
            })
        except Exception as e:
            print(f"Error processing service {service[1]}: {str(e)}")
            continue
            
    return render_template('index.html', services=formatted_services, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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

@app.route('/refresh/<service_name>', methods=['POST'])
def refresh_service(service_name):
    # Just return the current status of the service
    services = get_services()
    for service in services:
        if service[1] == service_name:  # service[1] is the name
            last_heartbeat = datetime.strptime(service[4], '%Y-%m-%d %H:%M:%S')
            time_diff = (datetime.now() - last_heartbeat).total_seconds()
            status = 'UP' if time_diff < 60 else 'DOWN'
            return jsonify({
                'name': service_name,
                'status': status,
                'last_heartbeat': service[4]
            }), 200
    return jsonify({'error': 'Service not found'}), 404

@app.route('/refresh_all', methods=['POST'])
def refresh_all_services():
    # Return current status of all services
    services = get_services()
    service_statuses = []
    for service in services:
        last_heartbeat = datetime.strptime(service[4], '%Y-%m-%d %H:%M:%S')
        time_diff = (datetime.now() - last_heartbeat).total_seconds()
        status = 'UP' if time_diff < 60 else 'DOWN'
        service_statuses.append({
            'name': service[1],
            'status': status,
            'last_heartbeat': service[4]
        })
    return jsonify({'services': service_statuses}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)

