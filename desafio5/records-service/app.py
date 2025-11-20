from flask import Flask, jsonify, request
import sys
import json
from datetime import datetime

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def log_info(message):
    print(message, flush=True)
    sys.stdout.flush()

def load_records():
    with open('records_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

records_db = load_records()

@app.route('/')
def home():
    return jsonify({
        'service': 'Records Service',
        'description': 'Vinyl Records Catalog Management',
        'version': '1.0',
        'endpoints': {
            'GET /records': 'Lista todos os discos do catálogo',
            'GET /records/<id>': 'Detalhes de um disco específico',
            'GET /records/genre/<genre>': 'Filtra discos por gênero',
            'GET /records/available': 'Lista apenas discos disponíveis',
            'PUT /records/<id>/decrease': 'Decrementa cópias disponíveis (aluguel)',
            'PUT /records/<id>/increase': 'Incrementa cópias disponíveis (devolução)',
            'GET /health': 'Health check do serviço'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'records-service',
        'total_records': len(records_db),
        'timestamp': datetime.now().isoformat()
    })

# Lista o catálogo de vinis
@app.route('/records', methods=['GET'])
def list_records():
    log_info("[RECORDS] Listando todo o catálogo de vinis...")
    log_info(f"[RECORDS] Total de discos no catálogo: {len(records_db)}")
    
    return jsonify({
        'total': len(records_db),
        'records': records_db
    })

@app.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    log_info(f"[RECORDS] Procurando disco #{record_id}...")
    
    record = next((r for r in records_db if r['id'] == record_id), None)
    
    if not record:
        log_info(f"[RECORDS] Disco {record_id} não encontrado")
        return jsonify({'error': 'Disco não encontrado'}), 404
    
    log_info(f"[RECORDS] Retornando: {record['title']} - {record['artist']}")
    return jsonify(record)

@app.route('/records/genre/<genre>', methods=['GET'])
def get_by_genre(genre):
    log_info(f"[RECORDS] Filtrando por gênero: {genre}")
    
    filtered = [r for r in records_db if r['genre'].lower() == genre.lower()]
    
    log_info(f"[RECORDS] Encontrados {len(filtered)} discos de {genre}")
    
    return jsonify({
        'genre': genre,
        'total': len(filtered),
        'records': filtered
    })

@app.route('/records/available', methods=['GET'])
def get_available():
    log_info("[RECORDS] Filtrando discos disponíveis...")
    
    available = [r for r in records_db if r['available_copies'] > 0]
    
    log_info(f"[RECORDS] {len(available)} discos disponíveis para aluguel")
    
    return jsonify({
        'total': len(available),
        'records': available
    })

@app.route('/records/<int:record_id>/decrease', methods=['PUT'])
def decrease_copies(record_id):
    log_info(f"[RECORDS] Alocando cópia do disco {record_id}...")
    
    record = next((r for r in records_db if r['id'] == record_id), None)
    
    if not record:
        return jsonify({'error': 'Disco não encontrado'}), 404
    
    if record['available_copies'] <= 0:
        log_info(f"[RECORDS] ERRO: Nenhuma cópia disponível de '{record['title']}'")
        return jsonify({'error': 'Nenhuma cópia disponível'}), 400
    
    record['available_copies'] -= 1
    
    log_info(f"[RECORDS] {record['title']}: {record['available_copies']}/{record['total_copies']} em estoque")
    
    return jsonify({
        'message': 'Cópia alocada para aluguel',
        'record': record['title'],
        'available_copies': record['available_copies']
    })

@app.route('/records/<int:record_id>/increase', methods=['PUT'])
def increase_copies(record_id):
    log_info(f"[RECORDS] Devolvendo cópia do disco {record_id}...")
    
    record = next((r for r in records_db if r['id'] == record_id), None)
    
    if not record:
        return jsonify({'error': 'Disco não encontrado'}), 404
    
    if record['available_copies'] >= record['total_copies']:
        log_info(f"[RECORDS] AVISO: Todas as cópias já estão disponíveis")
        return jsonify({'error': 'Todas as cópias já disponíveis'}), 400
    
    record['available_copies'] += 1
    
    log_info(f"[RECORDS] {record['title']}: {record['available_copies']}/{record['total_copies']} em estoque")
    
    return jsonify({
        'message': 'Cópia devolvida ao estoque',
        'record': record['title'],
        'available_copies': record['available_copies']
    })

if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando Records Service - Catálogo de Vinis")
    log_info("="*60)
    log_info(f"Total de discos no catálogo: {len(records_db)}")
    log_info("API rodando em http://0.0.0.0:5001")
    log_info("="*60)
    app.run(host='0.0.0.0', port=5001, debug=False)
