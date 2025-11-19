from flask import Flask, jsonify, request
import psycopg2
import redis
import json
import uuid
import os
import sys
import logging
from datetime import datetime

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def log_info(message):
    print(message, flush=True)
    sys.stdout.flush()

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'pokemon_db'),
    'user': os.getenv('DB_USER', 'trainer'),
    'password': os.getenv('DB_PASSWORD', 'pokeball')
}

# Configurações do Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'cache')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def calcular_dano(atacante, defensor):
    atk = max(atacante['ataque'], atacante['ataque_especial'])
    defe = max(defensor['defesa'], defensor['defesa_especial'])
    
    dano = max(5, int((atk * 2) / (defe * 0.5)))
    return dano

@app.route('/')
def home():
    return jsonify({
        'message': 'Sistema de Batalha Pokemon - Eeveelutions',
        'version': '1.0',
        'endpoints': {
            'GET /pokemon': 'Lista todos os Pokemon',
            'GET /pokemon/id': 'Detalhes de um Pokemon (com cache)',
            'POST /battle/start': 'Inicia e executa batalha completa {pokemon1_id, pokemon2_id}',
            'GET /history': 'Historico de batalhas'
        }
    })

# Listar todos os pokemo
@app.route('/pokemon', methods=['GET'])
def listar_pokemon():
    log_info("[BATTLE-API] Listando Pokemon...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    log_info("[BATTLE-API] Consultando PostgreSQL...")
    cursor.execute("SELECT * FROM pokemon ORDER BY id")
    pokemons = cursor.fetchall()
    
    resultado = []
    for p in pokemons:
        resultado.append({
            'id': p[0],
            'nome': p[1],
            'tipo': p[2],
            'hp': p[3],
            'ataque': p[4],
            'defesa': p[5],
            'ataque_especial': p[6],
            'defesa_especial': p[7],
            'velocidade': p[8]
        })
    
    cursor.close()
    conn.close()
    
    log_info(f"[BATTLE-API] {len(resultado)} Pokemon encontrados")
    return jsonify(resultado)

# Get Pokemon pelo id
@app.route('/pokemon/<int:pokemon_id>', methods=['GET'])
def obter_pokemon(pokemon_id):
    log_info(f"[BATTLE-API] Buscando Pokemon ID: {pokemon_id}")
    
    cache_key = f"pokemon:{pokemon_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        log_info(f"[REDIS] Cache HIT para Pokemon {pokemon_id}")
        return jsonify(json.loads(cached))
    
    log_info(f"[REDIS] Cache MISS para Pokemon {pokemon_id}")
    log_info("[BATTLE-API] Consultando PostgreSQL...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pokemon WHERE id = %s", (pokemon_id,))
    p = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not p:
        return jsonify({'error': 'Pokemon não encontrado'}), 404
    
    pokemon = {
        'id': p[0],
        'nome': p[1],
        'tipo': p[2],
        'hp': p[3],
        'ataque': p[4],
        'defesa': p[5],
        'ataque_especial': p[6],
        'defesa_especial': p[7],
        'velocidade': p[8]
    }
    
    log_info(f"[REDIS] Salvando Pokemon {pokemon_id} no cache")
    redis_client.setex(cache_key, 300, json.dumps(pokemon))
    
    return jsonify(pokemon)

# Iniciar Batalha Automatica
@app.route('/battle/start', methods=['POST'])
def iniciar_batalha():
    data = request.get_json()
    pokemon1_id = data.get('pokemon1_id')
    pokemon2_id = data.get('pokemon2_id')
    
    log_info(f"[BATTLE-API] Iniciando batalha: {pokemon1_id} vs {pokemon2_id}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    log_info("[BATTLE-API] Consultando PostgreSQL para Pokemon 1...")
    cursor.execute("SELECT * FROM pokemon WHERE id = %s", (pokemon1_id,))
    p1 = cursor.fetchone()
    
    log_info("[BATTLE-API] Consultando PostgreSQL para Pokemon 2...")
    cursor.execute("SELECT * FROM pokemon WHERE id = %s", (pokemon2_id,))
    p2 = cursor.fetchone()
    
    if not p1 or not p2:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Um ou ambos os Pokemon não encontrados'}), 404
    
    pokemon1 = {
        'id': p1[0], 'nome': p1[1], 'tipo': p1[2],
        'hp_atual': p1[3], 'hp_max': p1[3],
        'ataque': p1[4], 'defesa': p1[5],
        'ataque_especial': p1[6], 'defesa_especial': p1[7],
        'velocidade': p1[8]
    }
    
    pokemon2 = {
        'id': p2[0], 'nome': p2[1], 'tipo': p2[2],
        'hp_atual': p2[3], 'hp_max': p2[3],
        'ataque': p2[4], 'defesa': p2[5],
        'ataque_especial': p2[6], 'defesa_especial': p2[7],
        'velocidade': p2[8]
    }
    
    if pokemon1['velocidade'] >= pokemon2['velocidade']:
        atacante = pokemon1
        defensor = pokemon2
    else:
        atacante = pokemon2
        defensor = pokemon1
    
    log_info(f"[BATTLE-API] {atacante['nome']} (Speed: {atacante['velocidade']}) ataca primeiro!")
    
    turno = 0
    log_batalha = []
    
    while pokemon1['hp_atual'] > 0 and pokemon2['hp_atual'] > 0:
        turno += 1
        
        dano = calcular_dano(atacante, defensor)
        defensor['hp_atual'] = max(0, defensor['hp_atual'] - dano)
        
        log_entry = f"Turno {turno}: {atacante['nome']} ataca {defensor['nome']} causando {dano} de dano! HP restante: {defensor['hp_atual']}/{defensor['hp_max']}"
        log_batalha.append(log_entry)
        log_info(f"[BATTLE-API] {log_entry}")
        
        if defensor['hp_atual'] <= 0:
            vencedor = atacante
            perdedor = defensor
            break
        
        atacante, defensor = defensor, atacante
    
    log_info(f"[BATTLE-API] {vencedor['nome']} venceu após {turno} turnos!")
    
    log_info("[BATTLE-API] Salvando resultado no PostgreSQL...")
    cursor.execute(
        """INSERT INTO batalhas 
           (pokemon1_id, pokemon1_nome, pokemon2_id, pokemon2_nome, 
            vencedor_id, vencedor_nome, turnos)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           RETURNING id""",
        (pokemon1['id'], pokemon1['nome'],
         pokemon2['id'], pokemon2['nome'],
         vencedor['id'], vencedor['nome'], turno)
    )
    battle_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    log_info("[POSTGRES] Batalha salva no historico")
    
    return jsonify({
        'battle_id': battle_id,
        'pokemon1': pokemon1['nome'],
        'pokemon2': pokemon2['nome'],
        'vencedor': vencedor['nome'],
        'perdedor': perdedor['nome'],
        'turnos': turno,
        'log': log_batalha,
        'status': 'finalizada'
    })

# Historico de Batalhas
@app.route('/history', methods=['GET'])
def historico():
    log_info("[BATTLE-API] Consultando historico de batalhas no PostgreSQL...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, pokemon1_nome, pokemon2_nome, vencedor_nome, turnos, data_batalha
        FROM batalhas 
        ORDER BY data_batalha DESC 
        LIMIT 10
    """)
    batalhas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    resultado = []
    for b in batalhas:
        resultado.append({
            'id': b[0],
            'pokemon1': b[1],
            'pokemon2': b[2],
            'vencedor': b[3],
            'turnos': b[4],
            'data': b[5].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    log_info(f"[BATTLE-API] {len(resultado)} batalhas no historico")
    return jsonify(resultado)


if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando Battle API - Sistema de Batalha Pokemon")
    log_info("="*60)
    log_info(f"Conectando ao PostgreSQL: {DB_CONFIG['host']}")
    log_info(f"Conectando ao Redis: {REDIS_HOST}:{REDIS_PORT}")
    log_info("API rodando em http://0.0.0.0:5000")
    log_info("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False)
