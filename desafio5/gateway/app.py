from flask import Flask, jsonify, request
import sys
import requests
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

RECORDS_SERVICE_URL = "http://records-service:5001"
RENTALS_SERVICE_URL = "http://rentals-service:5002"

@app.route('/')
def home():
    return jsonify({
        'service': 'API Gateway',
        'description': 'Vinyl Records Rental Shop - Central Access Point',
        'version': '1.0',
        'architecture': 'API Gateway Pattern',
        'endpoints': {
            'GET /records': 'Lista catálogo de discos',
            'GET /records/<id>': 'Detalhes de um disco',
            'GET /records/genre/<genre>': 'Filtra por gênero',
            'GET /customers': 'Lista clientes',
            'GET /rentals': 'Lista aluguéis',
            'GET /rentals/active': 'Aluguéis ativos',
            'GET /records/<id>/availability': 'Disco + disponibilidade',
            'GET /customers/<id>/profile': 'Perfil completo + histórico',
            'POST /rent': 'Criar aluguel + atualizar estoque',
            'PUT /return/<rental_id>': 'Devolver + liberar estoque',
            'GET /recommendations/<customer_id>': 'Recomendações baseadas em histórico'
        }
    })

@app.route('/health')
def health():
    log_info("[GATEWAY] Verificando saúde dos microsserviços...")
    
    services_health = {}
    
    try:
        response = requests.get(f"{RECORDS_SERVICE_URL}/health", timeout=2)
        services_health['records_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_health['records_service'] = 'unavailable'
    
    try:
        response = requests.get(f"{RENTALS_SERVICE_URL}/health", timeout=2)
        services_health['rentals_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_health['rentals_service'] = 'unavailable'
    
    all_healthy = all(status == 'healthy' for status in services_health.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'gateway': 'healthy',
        'services': services_health,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/records', methods=['GET'])
def list_records():
    log_info("[GATEWAY] Buscando catálogo de discos...")
    
    try:
        response = requests.get(f"{RECORDS_SERVICE_URL}/records", timeout=5)
        response.raise_for_status()
        
        log_info(f"[GATEWAY] Pronto! Catálogo carregado")
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        log_info(f"[GATEWAY] ERRO: Serviço de Records indisponivel")
        return jsonify({
            'error': 'Serviço de discos está indisponivel',
            'details': str(e)
        }), 503

@app.route('/records/<int:record_id>', methods=['GET'])
def get_record(record_id):
    log_info(f"[GATEWAY] Procurando disco #{record_id}...")
    
    try:
        response = requests.get(f"{RECORDS_SERVICE_URL}/records/{record_id}", timeout=5)
        
        if response.status_code == 404:
            return jsonify({'error': 'Disco não encontrado'}), 404
        
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        log_info(f"[GATEWAY] ERRO: {str(e)}")
        return jsonify({'error': 'Records Service indisponível'}), 503

@app.route('/records/genre/<genre>', methods=['GET'])
def get_records_by_genre(genre):
    log_info(f"[GATEWAY] Roteando GET /records/genre/{genre}")
    
    try:
        response = requests.get(f"{RECORDS_SERVICE_URL}/records/genre/{genre}", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Records Service indisponível'}), 503


@app.route('/customers', methods=['GET'])
def list_customers():
    log_info("[GATEWAY] Roteando GET /customers")
    
    try:
        response = requests.get(f"{RENTALS_SERVICE_URL}/customers", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Rentals Service indisponível'}), 503

@app.route('/rentals', methods=['GET'])
def list_rentals():
    log_info("[GATEWAY] Roteando GET /rentals")
    
    try:
        response = requests.get(f"{RENTALS_SERVICE_URL}/rentals", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Rentals Service indisponível'}), 503

@app.route('/rentals/active', methods=['GET'])
def get_active_rentals():
    log_info("[GATEWAY] Roteando GET /rentals/active")
    
    try:
        response = requests.get(f"{RENTALS_SERVICE_URL}/rentals/active", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Rentals Service indisponível'}), 503



@app.route('/records/<int:record_id>/availability', methods=['GET'])
def get_record_availability(record_id):
    
    try:
        log_info(f"[GATEWAY] → GET {RECORDS_SERVICE_URL}/records/{record_id}")
        record_response = requests.get(f"{RECORDS_SERVICE_URL}/records/{record_id}", timeout=5)
        
        if record_response.status_code == 404:
            return jsonify({'error': 'Disco não encontrado'}), 404
        
        record_response.raise_for_status()
        record = record_response.json()
        
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/rentals/active")
        rentals_response = requests.get(f"{RENTALS_SERVICE_URL}/rentals/active", timeout=5)
        rentals_response.raise_for_status()
        active_rentals = rentals_response.json()['rentals']
        
        currently_rented_by = [
            r['customer_name'] for r in active_rentals 
            if r['record_id'] == record_id
        ]
        
        next_available = None
        if record['available_copies'] == 0 and currently_rented_by:
            due_dates = [r['due_date'] for r in active_rentals if r['record_id'] == record_id]
            if due_dates:
                next_available = min(due_dates)
        
        log_info("[GATEWAY] Agregação completa!")
        
        result = {
            'record': {
                'id': record['id'],
                'title': record['title'],
                'artist': record['artist'],
                'genre': record['genre'],
                'daily_price': record['daily_rental_price']
            },
            'availability': {
                'available_copies': record['available_copies'],
                'total_copies': record['total_copies'],
                'is_available': record['available_copies'] > 0,
                'currently_rented_by': currently_rented_by,
                'next_available': next_available
            }
        }
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        log_info(f"[GATEWAY] ERRO na agregação: {str(e)}")
        return jsonify({'error': 'Erro ao agregar dados dos serviços'}), 503

@app.route('/customers/<int:customer_id>/profile', methods=['GET'])
def get_customer_profile(customer_id):
    log_info("[GATEWAY] Montando perfil completo do cliente...")
    
    try:
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/customers/{customer_id}")
        customer_response = requests.get(f"{RENTALS_SERVICE_URL}/customers/{customer_id}", timeout=5)
        
        if customer_response.status_code == 404:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        customer_response.raise_for_status()
        customer = customer_response.json()
        
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/rentals/customer/{customer_id}")
        rentals_response = requests.get(f"{RENTALS_SERVICE_URL}/rentals/customer/{customer_id}", timeout=5)
        rentals_response.raise_for_status()
        rentals_data = rentals_response.json()
        
        active_rentals = [r for r in rentals_data['rentals'] if r['status'] == 'active']
        total_spent = sum(r['total_cost'] + r['late_fee'] for r in rentals_data['rentals'])
        
        log_info("[GATEWAY] Perfil agregado com sucesso!")
        
        result = {
            'customer': customer,
            'active_rentals': active_rentals,
            'statistics': {
                'total_rentals': rentals_data['total_rentals'],
                'active_count': len(active_rentals),
                'total_spent': round(total_spent, 2),
                'favorite_genre': customer['favorite_genre']
            },
            'fetched_from': ['rentals-service']
        }
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        log_info(f"[GATEWAY] ERRO: {str(e)}")
        return jsonify({'error': 'Erro ao montar perfil do cliente'}), 503

@app.route('/rent', methods=['POST'])
def create_rental():
    data = request.get_json()
    
    log_info("[GATEWAY] Iniciando processo de aluguel...")
    
    required_fields = ['customer_id', 'record_id', 'rental_days']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório: {field}'}), 400
    
    try:
        log_info(f"[GATEWAY] → GET {RECORDS_SERVICE_URL}/records/{data['record_id']}")
        record_response = requests.get(f"{RECORDS_SERVICE_URL}/records/{data['record_id']}", timeout=5)
        
        if record_response.status_code == 404:
            return jsonify({'error': 'Disco não encontrado'}), 404
        
        record_response.raise_for_status()
        record = record_response.json()
        
        if record['available_copies'] <= 0:
            log_info(f"[GATEWAY] ERRO: Disco '{record['title']}' sem cópias disponíveis")
            return jsonify({
                'error': 'Disco indisponível',
                'record': record['title'],
                'available_copies': 0
            }), 400
        
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/customers/{data['customer_id']}")
        customer_response = requests.get(f"{RENTALS_SERVICE_URL}/customers/{data['customer_id']}", timeout=5)
        
        if customer_response.status_code == 404:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        customer_response.raise_for_status()
        customer = customer_response.json()
        
        log_info(f"[GATEWAY] Validações OK! Cliente: {customer['name']}, Disco: {record['title']}")
        
        rental_data = {
            'customer_id': data['customer_id'],
            'record_id': data['record_id'],
            'record_title': record['title'],
            'daily_price': record['daily_rental_price'],
            'rental_days': data['rental_days']
        }
        
        log_info(f"[GATEWAY] → POST {RENTALS_SERVICE_URL}/rentals")
        rental_response = requests.post(
            f"{RENTALS_SERVICE_URL}/rentals",
            json=rental_data,
            timeout=5
        )
        
        if rental_response.status_code != 201:
            error_data = rental_response.json()
            return jsonify(error_data), rental_response.status_code
        
        rental_result = rental_response.json()
        
        log_info(f"[GATEWAY] → PUT {RECORDS_SERVICE_URL}/records/{data['record_id']}/decrease")
        decrease_response = requests.put(
            f"{RECORDS_SERVICE_URL}/records/{data['record_id']}/decrease",
            timeout=5
        )
        decrease_response.raise_for_status()
        
        log_info("[GATEWAY] Aluguel concluído")
        log_info(f"[GATEWAY] Aluguel #{rental_result['rental']['id']} registrado")
        
        return jsonify({
            'message': 'Aluguel realizado com sucesso',
            'rental': rental_result['rental'],
            'orchestrated_by': 'gateway'
        }), 201
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Falha ao processar aluguel',
            'details': str(e)
        }), 503

@app.route('/return/<int:rental_id>', methods=['PUT'])
def return_rental(rental_id):
    log_info("[GATEWAY] Processando devolução...")
    
    try:
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/rentals/{rental_id}")
        rental_response = requests.get(f"{RENTALS_SERVICE_URL}/rentals/{rental_id}", timeout=5)
        
        if rental_response.status_code == 404:
            return jsonify({'error': 'Aluguel não encontrado'}), 404
        
        rental_response.raise_for_status()
        rental = rental_response.json()
        
        if rental['status'] == 'returned':
            return jsonify({'error': 'Aluguel já foi devolvido'}), 400
        
        log_info(f"[GATEWAY] → PUT {RENTALS_SERVICE_URL}/rentals/{rental_id}/return")
        return_response = requests.put(
            f"{RENTALS_SERVICE_URL}/rentals/{rental_id}/return",
            timeout=5
        )
        return_response.raise_for_status()
        return_result = return_response.json()
        
        log_info(f"[GATEWAY] → PUT {RECORDS_SERVICE_URL}/records/{rental['record_id']}/increase")
        increase_response = requests.put(
            f"{RECORDS_SERVICE_URL}/records/{rental['record_id']}/increase",
            timeout=5
        )
        increase_response.raise_for_status()
        
        log_info("[GATEWAY] Devolução concluída!")
        log_info(f"[GATEWAY] '{rental['record_title']}' devolvido ao estoque")
        
        return jsonify({
            'message': 'Devolução processada com sucesso',
            'rental': return_result['rental'],
            'late_fee': return_result['late_fee'],
            'orchestrated_by': 'gateway'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Falha ao processar devolução',
            'details': str(e)
        }), 503

@app.route('/recommendations/<int:customer_id>', methods=['GET'])
def get_recommendations(customer_id):
    log_info("[GATEWAY] Preparando recomendações baseadas em historico...")
    
    try:
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/customers/{customer_id}")
        customer_response = requests.get(f"{RENTALS_SERVICE_URL}/customers/{customer_id}", timeout=5)
        
        if customer_response.status_code == 404:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        customer_response.raise_for_status()
        customer = customer_response.json()
        
        favorite_genre = customer['favorite_genre']
        log_info(f"[GATEWAY] Gênero favorito: {favorite_genre}")
        log_info(f"[GATEWAY] → GET {RECORDS_SERVICE_URL}/records/genre/{favorite_genre}")
        
        records_response = requests.get(f"{RECORDS_SERVICE_URL}/records/genre/{favorite_genre}", timeout=5)
        records_response.raise_for_status()
        genre_records = records_response.json()['records']
        
        available_recommendations = [r for r in genre_records if r['available_copies'] > 0]
        
        log_info(f"[GATEWAY] {len(available_recommendations)} recomendações encontradas")
        
        return jsonify({
            'customer': {
                'id': customer['id'],
                'name': customer['name'],
                'favorite_genre': favorite_genre
            },
            'recommendations': available_recommendations[:5],
            'total_available': len(available_recommendations),
            'generated_by': 'gateway'
        })
        
    except requests.exceptions.RequestException as e:
        log_info(f"[GATEWAY] ERRO: {str(e)}")
        return jsonify({'error': 'Falha ao gerar recomendações'}), 503

if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando API Gateway - Locadora de Discos de Vinil")
    log_info("="*60)
    log_info(f"Records Service: {RECORDS_SERVICE_URL}")
    log_info(f"Rentals Service: {RENTALS_SERVICE_URL}")
    log_info("Gateway rodando em http://0.0.0.0:8080")
    log_info("="*60)
    app.run(host='0.0.0.0', port=8080, debug=False)
