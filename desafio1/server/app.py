from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Contador de requisições
request_count = 0

@app.route('/')
def home():
    global request_count
    request_count += 1
    
    response_data = {
        'message': 'Servidor Flask em andamento!',
        'timestamp': datetime.now().isoformat(),
        'request_number': request_count,
        'container_name': os.getenv('HOSTNAME', 'unknown'),
        'status': 'running',
        'port': 8080
    }
    
    # Log no servidor
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Requisição #{request_count} recebida")
    
    return jsonify(response_data), 200

# Health do servidor
@app.route('/health')
def health():
    return jsonify(
        {
            'status': 'healthy', 
            'service': 'flask-server'
        }), 200

# Estatísticas do servidor
@app.route('/stats')
def stats():
    return jsonify({
        'total_requests': request_count,
        'uptime_message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("Começando servidor Flask na porta 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)