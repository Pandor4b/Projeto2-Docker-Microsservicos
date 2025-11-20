from flask import Flask, jsonify, request
import sys
import json
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def log_info(message):
    print(message, flush=True)
    sys.stdout.flush()

def load_customers():
    with open('customers_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rentals():
    with open('rentals_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

customers_db = load_customers()
rentals_db = load_rentals()

@app.route('/')
def home():
    return jsonify({
        'service': 'Rentals Service',
        'description': 'Vinyl Records Rental Management',
        'version': '1.0',
        'endpoints': {
            'GET /customers': 'Lista todos os clientes',
            'GET /customers/<id>': 'Detalhes de um cliente',
            'GET /rentals': 'Lista todos os alugueis',
            'GET /rentals/<id>': 'Detalhes de um aluguel',
            'GET /rentals/active': 'Lista alugueis ativos',
            'GET /rentals/customer/<customer_id>': 'Alugueis de um cliente',
            'POST /rentals': 'Criar novo aluguel',
            'PUT /rentals/<id>/return': 'Registrar devolução',
            'GET /health': 'Health check do serviço'
        }
    })

@app.route('/health')
def health():
    active_rentals = len([r for r in rentals_db if r['status'] == 'active'])
    return jsonify({
        'status': 'healthy',
        'service': 'rentals-service',
        'total_customers': len(customers_db),
        'total_rentals': len(rentals_db),
        'active_rentals': active_rentals,
        'timestamp': datetime.now().isoformat()
    })

# Listando todos os clientes
@app.route('/customers', methods=['GET'])
def list_customers():
    log_info("[RENTALS] Listando todos os clientes...")
    log_info(f"[RENTALS] Total de clientes cadastrados: {len(customers_db)}")
    
    return jsonify({
        'total': len(customers_db),
        'customers': customers_db
    })

# Lista cliente pelo ID
@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    log_info(f"[RENTALS] Procurando cliente #{customer_id}...")
    
    customer = next((c for c in customers_db if c['id'] == customer_id), None)
    
    if not customer:
        log_info(f"[RENTALS] Cliente {customer_id} não encontrado")
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    log_info(f"[RENTALS] Encontrado: {customer['name']} ({customer['membership_tier']})")
    return jsonify(customer)

# Lista registro de alugueis
@app.route('/rentals', methods=['GET'])
def list_rentals():
    log_info("[RENTALS] Listando todos os alugueis...")
    log_info(f"[RENTALS] Total de alugueis registrados: {len(rentals_db)}")
    
    return jsonify({
        'total': len(rentals_db),
        'rentals': rentals_db
    })

# Lista aluguel pelo ID
@app.route('/rentals/<int:rental_id>', methods=['GET'])
def get_rental(rental_id):
    log_info(f"[RENTALS] Buscando aluguel ID: {rental_id}")
    
    rental = next((r for r in rentals_db if r['id'] == rental_id), None)
    
    if not rental:
        log_info(f"[RENTALS] Aluguel {rental_id} não encontrado")
        return jsonify({'error': 'Aluguel não encontrado'}), 404
    
    log_info(f"[RENTALS] Retornando: {rental['record_title']} alugado por {rental['customer_name']}")
    return jsonify(rental)

# Filtra pelos alugueis ativos 
@app.route('/rentals/active', methods=['GET'])
def get_active_rentals():
    log_info("[RENTALS] Filtrando alugueis ativos...")
    
    active = [r for r in rentals_db if r['status'] == 'active']
    
    log_info(f"[RENTALS] {len(active)} alugueis ativos no momento")
    
    return jsonify({
        'total': len(active),
        'rentals': active
    })

# Lista historico de alugueis pelo id do cliente
@app.route('/rentals/customer/<int:customer_id>', methods=['GET'])
def get_customer_rentals(customer_id):
    log_info(f"[RENTALS] Buscando histórico de alugueis do cliente {customer_id}")
    
    customer = next((c for c in customers_db if c['id'] == customer_id), None)
    
    if not customer:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    customer_rentals = [r for r in rentals_db if r['customer_id'] == customer_id]
    active = [r for r in customer_rentals if r['status'] == 'active']
    
    log_info(f"[RENTALS] Cliente {customer['name']}: {len(customer_rentals)} alugueis, {len(active)} ativos")
    
    return jsonify({
        'customer_id': customer_id,
        'customer_name': customer['name'],
        'total_rentals': len(customer_rentals),
        'active_rentals': len(active),
        'rentals': customer_rentals
    })

# Criar aluguel
@app.route('/rentals', methods=['POST'])
def create_rental():
    data = request.get_json()
    
    log_info(f"[RENTALS] Registrando novo aluguel...")
    
    required_fields = ['customer_id', 'record_id', 'record_title', 'daily_price', 'rental_days']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
    
    customer = next((c for c in customers_db if c['id'] == data['customer_id']), None)
    
    if not customer:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    active_count = len([r for r in rentals_db if r['customer_id'] == data['customer_id'] and r['status'] == 'active'])
    
    if active_count >= customer['max_rentals']:
        log_info(f"[RENTALS] ERRO: Cliente {customer['name']} atingiu limite de {customer['max_rentals']} alugueis")
        return jsonify({
            'error': 'Limite de alugueis atingido',
            'current': active_count,
            'max': customer['max_rentals']
        }), 400
    
    new_id = max([r['id'] for r in rentals_db]) + 1 if rentals_db else 1
    
    rented_at = datetime.now()
    due_date = rented_at + timedelta(days=data['rental_days'])
    total_cost = data['daily_price'] * data['rental_days']
    
    new_rental = {
        'id': new_id,
        'customer_id': data['customer_id'],
        'customer_name': customer['name'],
        'record_id': data['record_id'],
        'record_title': data['record_title'],
        'rented_at': rented_at.strftime('%Y-%m-%d'),
        'due_date': due_date.strftime('%Y-%m-%d'),
        'returned_at': None,
        'daily_price': data['daily_price'],
        'rental_days': data['rental_days'],
        'total_cost': round(total_cost, 2),
        'status': 'active',
        'late_fee': 0.00
    }
    
    rentals_db.append(new_rental)
    customer['active_rentals'] += 1
    
    log_info(f"[RENTALS] Aluguel #{new_id} registrado com sucesso!")
    log_info(f"[RENTALS] {customer['name']} alugou '{data['record_title']}' por {data['rental_days']} dias")
    log_info(f"[RENTALS] Total: R$ {total_cost:.2f}")
    
    return jsonify({
        'message': 'Aluguel criado com sucesso',
        'rental': new_rental
    }), 201

# "Retorno" do vinyl alugado
@app.route('/rentals/<int:rental_id>/return', methods=['PUT'])
def return_rental(rental_id):
    log_info(f"[RENTALS] Recebendo devolução do aluguel #{rental_id}...")
    
    rental = next((r for r in rentals_db if r['id'] == rental_id), None)
    
    if not rental:
        return jsonify({'error': 'Aluguel não encontrado'}), 404
    
    if rental['status'] == 'returned':
        log_info(f"[RENTALS] AVISO: Aluguel {rental_id} já foi devolvido")
        return jsonify({'error': 'Aluguel já foi devolvido'}), 400
    
    returned_at = datetime.now()
    due_date = datetime.strptime(rental['due_date'], '%Y-%m-%d')
    
    late_fee = 0.00
    if returned_at > due_date:
        days_late = (returned_at - due_date).days
        late_fee = days_late * rental['daily_price']
        log_info(f"[RENTALS] ATRASO: {days_late} dias - Multa: R$ {late_fee:.2f}")
    
    rental['returned_at'] = returned_at.strftime('%Y-%m-%d')
    rental['status'] = 'returned'
    rental['late_fee'] = round(late_fee, 2)
    
    customer = next((c for c in customers_db if c['id'] == rental['customer_id']), None)
    if customer:
        customer['active_rentals'] -= 1
    
    log_info(f"[RENTALS] Devolução concluída: {rental['record_title']}")
    log_info(f"[RENTALS] Cliente: {rental['customer_name']}")
    
    return jsonify({
        'message': 'Devolução registrada com sucesso',
        'rental': rental,
        'late_fee': late_fee
    })

if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando Rentals Service - Gestão de Alugueis")
    log_info("="*60)
    log_info(f"Clientes cadastrados: {len(customers_db)}")
    log_info(f"Total de alugueis: {len(rentals_db)}")
    log_info("API rodando em http://0.0.0.0:5002")
    log_info("="*60)
    app.run(host='0.0.0.0', port=5002, debug=False)
