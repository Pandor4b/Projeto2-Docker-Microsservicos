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

def load_characters():
    with open('characters_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

characters_db = load_characters()

# Retorna todos os endpoints disponiveis
@app.route('/')
def home():
    return jsonify({
        'service': 'Characters Service',
        'description': "Don't Starve Together - Character Management",
        'version': '1.0',
        'endpoints': {
            'GET /characters': 'Lista todos os personagens do servidor',
            'GET /characters/<id>': 'Detalhes de um personagem específico',
            'GET /characters/odds/<level>': 'Filtra personagens por survival odds (Slim, Grim, None)',
            'POST /characters': 'Adiciona novo personagem ao servidor',
            'GET /health': 'Health check do serviço'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'characters-service',
        'total_characters': len(characters_db),
        'timestamp': datetime.now().isoformat()
    })

# Listar Personagens
@app.route('/characters', methods=['GET'])
def list_characters():
    log_info("[CHARACTERS] Listando todos os personagens...")
    log_info(f"[CHARACTERS] Total de personagens no servidor: {len(characters_db)}")
    
    return jsonify({
        'total': len(characters_db),
        'characters': characters_db
    })

# Listar Detalhes do Personagem pelo ID
@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    log_info(f"[CHARACTERS] Buscando personagem ID: {character_id}")
    
    character = next((c for c in characters_db if c['id'] == character_id), None)
    
    if not character:
        log_info(f"[CHARACTERS] Personagem {character_id} nao encontrado")
        return jsonify({'error': 'Personagem nao encontrado'}), 404
    
    log_info(f"[CHARACTERS] Retornando dados: {character['name']} - {character['title']}")
    return jsonify(character)

# Filtrando personagens pelas odds
@app.route('/characters/odds/<odds>', methods=['GET'])
def get_by_survival_odds(odds):
    log_info(f"[CHARACTERS] Filtrando por survival odds: {odds}")
    
    odds = odds.capitalize()
    
    if odds not in ['Slim', 'Grim', 'None']:
        return jsonify({'error': 'Survival odds inválido. Use: Slim, Grim ou None'}), 400
    
    filtered = [c for c in characters_db if c['survival_odds'] == odds]
    
    log_info(f"[CHARACTERS] Encontrados {len(filtered)} personagens com survival odds {odds}")
    
    return jsonify({
        'survival_odds': odds,
        'total': len(filtered),
        'characters': filtered
    })

# Adicionar novo personagem ao servidor
@app.route('/characters', methods=['POST'])
def add_character():
    data = request.get_json()
    
    log_info(f"[CHARACTERS] Adicionando novo personagem: {data.get('name', 'Unknown')}")
    
    required_fields = ['name', 'title', 'health', 'hunger', 'sanity', 'special_ability', 'survival_odds']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo obrigatório ausente: {field}'}), 400
    
    new_id = max([c['id'] for c in characters_db]) + 1 if characters_db else 1
    
    new_character = {
        'id': new_id,
        'name': data['name'],
        'title': data['title'],
        'health': data['health'],
        'hunger': data['hunger'],
        'sanity': data['sanity'],
        'special_ability': data['special_ability'],
        'survival_odds': data['survival_odds'],
        'joined_at': data.get('joined_at', datetime.now().strftime('%Y-%m-%d'))
    }
    
    characters_db.append(new_character)
    
    log_info(f"[CHARACTERS] Personagem adicionado com ID: {new_id}")
    log_info(f"[CHARACTERS] {new_character['name']} - {new_character['title']}")
    
    return jsonify({
        'message': 'Personagem adicionado com sucesso',
        'character': new_character
    }), 201

if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando Characters Service - Don't Starve Together")
    log_info("="*60)
    log_info(f"Total de personagens carregados: {len(characters_db)}")
    log_info("API rodando em http://0.0.0.0:5001")
    log_info("="*60)
    app.run(host='0.0.0.0', port=5001, debug=False)
