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

CHARACTERS_SERVICE_URL = "http://characters-service:5001"

def calculate_days_survived(joined_at):
    try:
        joined_date = datetime.strptime(joined_at, '%Y-%m-%d')
        today = datetime.now()
        delta = today - joined_date
        return delta.days
    except:
        return 0

def calculate_survival_rating(days):
    if days < 30:
        return "Novice Survivor"
    elif days < 100:
        return "Survivor"
    elif days < 200:
        return "Experienced Survivor"
    elif days < 365:
        return "Veteran of The Constant"
    else:
        return "Master of The Constant"

def calculate_survivability_score(health, hunger, sanity):
    total_stats = health + hunger + sanity
    base_score = total_stats / 50
    return round(min(10.0, base_score), 1)

def assess_risks(health, hunger, sanity):
    risks = {}
    
    # Avaliação de fome
    if hunger >= 200:
        risks['hunger_risk'] = "Very Low"
    elif hunger >= 150:
        risks['hunger_risk'] = "Low"
    elif hunger >= 100:
        risks['hunger_risk'] = "Medium"
    else:
        risks['hunger_risk'] = "High"
    
    # Avaliação de sanidade
    if sanity >= 200:
        risks['sanity_risk'] = "Very Low"
    elif sanity >= 150:
        risks['sanity_risk'] = "Low"
    elif sanity >= 100:
        risks['sanity_risk'] = "Medium"
    else:
        risks['sanity_risk'] = "High"
    
    # Avaliação de saúde
    if health >= 175:
        risks['health_risk'] = "Very Low"
    elif health >= 150:
        risks['health_risk'] = "Low"
    elif health >= 100:
        risks['health_risk'] = "Medium"
    else:
        risks['health_risk'] = "High"
    
    # Risco geral
    risk_values = list(risks.values())
    if risk_values.count("High") >= 2:
        risks['overall_risk'] = "Critical"
    elif "High" in risk_values:
        risks['overall_risk'] = "Elevated"
    elif risk_values.count("Medium") >= 2:
        risks['overall_risk'] = "Moderate"
    else:
        risks['overall_risk'] = "Stable"
    
    return risks

def generate_recommendations(character, risks):
    recommendations = []
    
    # Recomendações de fome
    if character['hunger'] >= 200:
        recommendations.append("Hight hunger, can sustain long expeditions")
    elif character['hunger'] >= 150:
        recommendations.append("Good hunger management")
    elif character['hunger'] < 100:
        recommendations.append("Prioritize food gathering and cooking")
    
    # Recomendações de sanidade
    if character['sanity'] >= 200:
        recommendations.append("Hight sanity, safe for shadow creature farming")
    elif character['sanity'] >= 150:
        recommendations.append("Decent sanity reserves")
    elif character['sanity'] < 120:
        recommendations.append("Craft Sanity-restoring items (Jerky, Cooked Green Cap, Taffy)")
    
    # Recomendações de saúde 
    if character['health'] >= 175:
        recommendations.append("High health pool - excellent for combat")
    elif character['health'] >= 150:
        recommendations.append("Standard health capacity")
    elif character['health'] < 100:
        recommendations.append("Craft Healing Salves or Honey Poultice")
    
    # Recomendações específicas do personagem
    if character['name'] == "WX-78":
        recommendations.append("Is Seeking lightning strikes for stat upgrades")
    
    if character['name'] == "Warly":
        recommendations.append("Is cooking gourmet meals for powerful buffs")
    
    if character['name'] == "Wormwood":
        recommendations.append("Is avoiding the fire damage from the Dragonfly")
    
    if character['name'] == "Wigfrid":
        recommendations.append("Is crafting battle helms and spears for combat agains The Dragonfly")
    
    # Recomendação geral
    if risks['overall_risk'] == "Stable":
        recommendations.append("Character is in good condition for exploration")
    elif risks['overall_risk'] == "Critical":
        recommendations.append("Focus on basic survival needs immediately")
    
    return recommendations

# Retorna uma lista com os endpoints disponíveis
@app.route('/')
def home():
    return jsonify({
        'service': 'Survival Stats Service',
        'description': "Don't Starve Together - Survival Analysis & Statistics",
        'version': '1.0',
        'endpoints': {
            'GET /survival-stats': 'Estatísticas de sobrevivência de todos os personagens',
            'GET /survival-stats/<id>': 'Análise detalhada de sobrevivência de um personagem',
            'GET /server-overview': 'Visão geral do servidor com estatísticas agregadas',
            'GET /health': 'Health check do serviço'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'survival-service',
        'timestamp': datetime.now().isoformat()
    })

# Lista os status de sobrevivencia de todos os perosnagens
@app.route('/survival-stats', methods=['GET'])
def list_survival_stats():
    log_info("[SURVIVAL-STATS] Listando survival stats de todos os personagens...")
    log_info("[SURVIVAL-STATS] Consultando Characters Service...")
    
    try:
        url = f"{CHARACTERS_SERVICE_URL}/characters"
        log_info(f"[SURVIVAL-STATS] HTTP GET → {url}")
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        characters = data.get('characters', [])
        
        log_info(f"[SURVIVAL-STATS] Recebidos {len(characters)} personagens")
        
        survival_stats = []
        
        for char in characters:
            days = calculate_days_survived(char['joined_at'])
            rating = calculate_survival_rating(days)
            score = calculate_survivability_score(char['health'], char['hunger'], char['sanity'])
            
            survival_stats.append({
                'id': char['id'],
                'name': char['name'],
                'title': char['title'],
                'days_survived': days,
                'survival_rating': rating,
                'survivability_score': score,
                'status': f"Surviving for {days} days in The Constant"
            })
        
        log_info(f"[SURVIVAL-STATS] Processados {len(survival_stats)} survival stats")
        
        return jsonify({
            'total': len(survival_stats),
            'survival_stats': survival_stats,
            'fetched_from': 'characters-service'
        })
        
    except requests.exceptions.RequestException as e:
        log_info(f"[SURVIVAL-STATS] ERRO ao conectar com Characters Service: {str(e)}")
        return jsonify({
            'error': 'Characters Service indisponivel',
            'message': 'Não foi possível obter dados dos personagens',
            'details': str(e)
        }), 503

# Lista dados detalhados de um perosnagem pelo ID
@app.route('/survival-stats/<int:character_id>', methods=['GET'])
def get_survival_stats(character_id):
    log_info(f"[SURVIVAL-STATS] Consultando survival stats para personagem ID: {character_id}")
    log_info("[SURVIVAL-STATS] Consultando Characters Service...")
    
    try:
        url = f"{CHARACTERS_SERVICE_URL}/characters/{character_id}"
        log_info(f"[SURVIVAL-STATS] HTTP GET → {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 404:
            log_info(f"[SURVIVAL-STATS] Personagem {character_id} não encontrado")
            return jsonify({'error': 'Personagem não encontrado'}), 404
        
        response.raise_for_status()
        character = response.json()
        
        log_info(f"[SURVIVAL-STATS] Recebidos dados de: {character['name']}")
        
        days = calculate_days_survived(character['joined_at'])
        rating = calculate_survival_rating(days)
        score = calculate_survivability_score(character['health'], character['hunger'], character['sanity'])
        risks = assess_risks(character['health'], character['hunger'], character['sanity'])
        recommendations = generate_recommendations(character, risks)
        
        log_info(f"[SURVIVAL-STATS] Calculando dias sobrevividos: {days} dias")
        log_info(f"[SURVIVAL-STATS] Survival rating: {rating}")
        log_info(f"[SURVIVAL-STATS] Survivability score: {score}/10")
        log_info(f"[SURVIVAL-STATS] Avaliando riscos... Status: {risks['overall_risk']}")
        
        result = {
            'id': character['id'],
            'name': character['name'],
            'title': character['title'],
            'base_stats': {
                'health': character['health'],
                'hunger': character['hunger'],
                'sanity': character['sanity']
            },
            'special_ability': character['special_ability'],
            'survival_odds': character['survival_odds'],
            'survival_info': {
                'days_survived': days,
                'survival_rating': rating,
                'total_stat_points': character['health'] + character['hunger'] + character['sanity'],
                'survivability_score': score,
                'status': f"Thriving - {days} days in The Constant"
            },
            'risk_assessment': risks,
            'recommendations': recommendations,
            'joined_at': character['joined_at'],
            'fetched_from': 'characters-service',
            'calculated_at': datetime.now().isoformat()
        }
        
        log_info("[SURVIVAL-STATS] Retornando survival stats completo")
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        log_info(f"[SURVIVAL-STATS] ERRO ao conectar com Characters Service: {str(e)}")
        return jsonify({
            'error': 'Characters Service indisponivel',
            'message': 'Não foi possível obter dados do personagem',
            'details': str(e)
        }), 503

# Visão geral do servidor
@app.route('/server-overview', methods=['GET'])
def server_overview():
    log_info("[SURVIVAL-STATS] Gerando visão geral do servidor...")
    log_info("[SURVIVAL-STATS] Consultando Characters Service...")
    
    try:
        url = f"{CHARACTERS_SERVICE_URL}/characters"
        log_info(f"[SURVIVAL-STATS] HTTP GET → {url}")
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        characters = data.get('characters', [])
        
        if not characters:
            return jsonify({
                'message': 'Nenhum personagem no servidor',
                'total_characters': 0
            })
        
        total_chars = len(characters)
        avg_health = sum(c['health'] for c in characters) / total_chars
        avg_hunger = sum(c['hunger'] for c in characters) / total_chars
        avg_sanity = sum(c['sanity'] for c in characters) / total_chars
        
        odds_distribution = {}
        for char in characters:
            odds = char['survival_odds']
            odds_distribution[odds] = odds_distribution.get(odds, 0) + 1
        
        total_days = sum(calculate_days_survived(c['joined_at']) for c in characters)
        
        log_info(f"[SURVIVAL-STATS] Servidor com {total_chars} personagens")
        log_info(f"[SURVIVAL-STATS] Total acumulado: {total_days} dias sobrevividos")
        
        return jsonify({
            'server_statistics': {
                'total_characters': total_chars,
                'total_days_survived': total_days,
                'average_stats': {
                    'health': round(avg_health, 1),
                    'hunger': round(avg_hunger, 1),
                    'sanity': round(avg_sanity, 1)
                },
                'survival_odds_distribution': odds_distribution,
                'server_status': 'Active and Thriving'
            },
            'fetched_from': 'characters-service',
            'generated_at': datetime.now().isoformat()
        })
        
    except requests.exceptions.RequestException as e:
        log_info(f"[SURVIVAL-STATS] ERRO ao conectar com Characters Service: {str(e)}")
        return jsonify({
            'error': 'Characters Service indisponivel',
            'message': 'Não foi possível gerar visão geral do servidor'
        }), 503

if __name__ == '__main__':
    log_info("="*60)
    log_info("Iniciando Survival Stats Service")
    log_info("="*60)
    log_info(f"Characters Service URL: {CHARACTERS_SERVICE_URL}")
    log_info("API rodando em http://0.0.0.0:5002")
    log_info("="*60)
    app.run(host='0.0.0.0', port=5002, debug=False)
