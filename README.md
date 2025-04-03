# Service Registry Monitor

A lightweight service registry and monitoring system that tracks the status of various services in real-time. Built with Python Flask and SQLite, it provides a clean web interface to monitor service health and status. This system is particularly useful for microservices architectures where you need to track the availability of multiple services.

## Features

- Real-time service status monitoring with visual indicators
- Automatic service cleanup for stale services (60-second timeout)
- Modern web interface with Bootstrap and Font Awesome icons
- Individual and bulk service status refresh
- RESTful API endpoints for service registration and status checks
- SQLite database for persistent storage
- Auto-refresh functionality (30-second intervals)
- Error handling and logging
- Microsecond-precise heartbeat tracking

## Prerequisites

- Python 3.x
- Flask (`pip install flask`)
- SQLite3 (comes with Python)
- Web browser for accessing the monitoring interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd service-registry-server
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install flask
```

## Project Structure

```
service-registry-server/
├── monitor.py           # Main application file
├── monitoring.db        # SQLite database (created automatically)
└── templates/
    └── index.html      # Web interface template
```

## Running the Application

1. Start the server:
```bash
python monitor.py
```

2. Access the web interface at:
```
http://localhost:5001
```

## API Endpoints

### Register a Service
- **URL**: `/register`
- **Method**: `POST`
- **Body**:
```json
{
    "name": "service-name",
    "ip": "service-ip"
}
```
- **Example**:
```bash
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"name": "auth-service", "ip": "192.168.1.100"}'
```

### Get All Services
- **URL**: `/services`
- **Method**: `GET`
- **Example**:
```bash
curl http://localhost:5001/services
```

### Refresh Service Status
- **URL**: `/refresh/<service_name>`
- **Method**: `POST`
- **Example**:
```bash
curl -X POST http://localhost:5001/refresh/auth-service
```

### Refresh All Services
- **URL**: `/refresh_all`
- **Method**: `POST`
- **Example**:
```bash
curl -X POST http://localhost:5001/refresh_all
```

## Web Interface Features

- Clean, responsive design that works on all devices
- Real-time status updates without page reload
- Individual service refresh buttons for targeted updates
- Bulk refresh option for updating all services at once
- Auto-refresh every 30 seconds
- Color-coded status indicators (green for UP, red for DOWN)
- Last heartbeat timestamps with microsecond precision
- Error handling and user feedback

## Service Status Logic

- A service is considered **UP** if it has sent a heartbeat within the last 60 seconds
- A service is considered **DOWN** if no heartbeat is received for more than 60 seconds
- Stale services (no heartbeat for >60 seconds) are automatically removed from the registry
- Status is calculated based on the difference between current time and last heartbeat
- Microsecond precision in timestamp tracking

## Database Schema

```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ip TEXT NOT NULL,
    status TEXT NOT NULL,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Usage Examples

### Registering a New Service
```python
import requests

response = requests.post(
    'http://localhost:5001/register',
    json={
        'name': 'payment-service',
        'ip': '192.168.1.101'
    }
)
print(response.json())
```

### Checking Service Status
```python
import requests

response = requests.get('http://localhost:5001/services')
services = response.json()['services']
for service in services:
    print(f"Service: {service['name']}, Status: {service['status']}")
```

## Troubleshooting

1. **Service Not Showing Up**
   - Check if the service registration request was successful
   - Verify the service name and IP in the registration request
   - Check the server logs for any errors

2. **Status Not Updating**
   - Ensure the service is sending heartbeats regularly
   - Check if the service is within the 60-second timeout period
   - Verify the network connectivity between services

3. **Database Issues**
   - If the database becomes corrupted, delete the monitoring.db file
   - The system will automatically create a new database on restart

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.