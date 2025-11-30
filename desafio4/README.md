# Desafio 4 — Microsserviços Independentes

## 📋 Descrição do Projeto

Sistema de gerenciamento de personagens e análise de sobrevivência para **Don't Starve Together**. Demonstra comunicação HTTP entre dois microsserviços independentes.

---

## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🔍 Como Funciona](#-como-funciona) • [🎮 Personagens](#-personagens-disponíveis) • [🚀 Executar](#-como-executar) • [📊 Endpoints](#-endpoints-dos-microsserviços) • [🧪 Testes](#-testando-os-microsserviços)

---

## 🏗️ Arquitetura da Solução

```
┌────────────────────────────────────────────────────────┐
│              MICROSSERVIÇOS - DST SERVER               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────┐                     │
│  │  Microsserviço A             │                     │
│  │  Characters Service          │                     │
│  │  Port: 5001                  │                     │
│  │                               │                     │
│  │  Gerencia personagens e      │                     │
│  │  estatísticas base           │                     │
│  └──────────────┬───────────────┘                     │
│                 │                                      │
│                 │ HTTP GET                             │
│                 │ /characters                          │
│                 │ /characters/{id}                     │
│                 │                                      │
│                 ↓                                      │
│  ┌─────────────────────────────┐                     │
│  │  Microsserviço B             │                     │
│  │  Survival Stats Service      │                     │
│  │  Port: 5002                  │                     │
│  │                               │                     │
│  │  Consome dados do Serviço A  │                     │
│  │  Calcula survival stats      │                     │
│  │  Gera recomendações          │                     │
│  └─────────────────────────────┘                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 🔧 Tecnologias Utilizadas

- **Docker**: Containerização, orquestração e redes
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web para API REST
- **Requests**: Biblioteca HTTP para comunicação entre serviços

## 📁 Estrutura do Projeto

```
desafio4/
├── characters-service/          # Microsserviço A
│   ├── app.py                   # API REST de personagens
│   ├── characters_data.json     # Dados dos personagens
│   ├── Dockerfile
│   └── requirements.txt
├── survival-service/            # Microsserviço B
│   ├── app.py                   # API de análise de sobrevivência
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml           # Orquestração dos 2 microsserviços
└── README.md
```

## 🔍 Como Funciona

### 1. Arquitetura de Microsserviços Independentes

#### Microsserviço A: Characters Service (Porta 5001)

**Responsabilidade:** Gerenciar dados de personagens

```python

# Carrega dados do JSON
def load_characters():
    with open('characters_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

characters_db = load_characters() 
```

**Estrutura dos dados:**

```json
{
  "id": 1,
  "name": "Wilson",
  "title": "The Gentleman Scientist",
  "health": 150,
  "hunger": 150,
  "sanity": 200,
  "special_ability": "Grows a Magnificent Beard",
  "survival_odds": "Grim",
  "joined_at": "2023-01-15"
}
```

**Endpoints principais:**

1. **GET /characters** - Lista todos os personagens
2. **GET /characters/<id>** - Detalhes de um personagem específico
3. **GET /characters/odds/<level>** - Filtra por survival odds
4. **POST /characters** - Adiciona novo personagem

**Não possui dependências externas:**
- Não conecta a banco de dados
- Não chama outros microsserviços
- Auto-contido e independente

#### Microsserviço B: Survival Service (Porta 5002)

**Responsabilidade:** Análise de sobrevivência baseada em dados do Characters Service

```python
# survival-service/app.py

CHARACTERS_SERVICE_URL = "http://characters-service:5001"

# Consome dados do Microsserviço A
response = requests.get(f"{CHARACTERS_SERVICE_URL}/characters")
characters = response.json()['characters']
```

**Dependência explícita:**
- Consome API do Characters Service via HTTP
- Adiciona lógica de negócio: cálculos, análises e recomendações
- Enriquece os dados originais

**Endpoints principais:**

1. **GET /survival-stats** - Análise de todos os personagens
2. **GET /survival-stats/<id>** - Análise detalhada de um personagem
3. **GET /server-overview** - Estatísticas agregadas do servidor

### 2. Comunicação HTTP entre Microsserviços

#### Fluxo: Endpoint `/survival-stats/<id>`

**Passo 1: Cliente faz requisição**

```bash
curl http://localhost:5002/survival-stats/1
```

**Passo 2: Survival Service recebe requisição**

```python
@app.route('/survival-stats/<int:character_id>', methods=['GET'])
def get_survival_stats(character_id):
    log_info(f"[SURVIVAL-STATS] Consultando survival stats para personagem ID: {character_id}")
    log_info("[SURVIVAL-STATS] Consultando Characters Service...")
```

**Passo 3: Survival Service chama Characters Service**

```python
    try:
        url = f"{CHARACTERS_SERVICE_URL}/characters/{character_id}"
        # http://characters-service:5001/characters/1
        
        log_info(f"[SURVIVAL-STATS] HTTP GET → {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 404:
            return jsonify({'error': 'Personagem não encontrado'}), 404
        
        response.raise_for_status()
        character = response.json()
```

**Requisição HTTP real:**

```http
GET /characters/1 HTTP/1.1
Host: characters-service:5001
User-Agent: python-requests/2.31.0
Accept: application/json
Connection: keep-alive
```

**Resposta do Characters Service:**

```json
{
  "id": 1,
  "name": "Wilson",
  "title": "The Gentleman Scientist",
  "health": 150,
  "hunger": 150,
  "sanity": 200,
  "special_ability": "Grows a Magnificent Beard",
  "survival_odds": "Grim",
  "joined_at": "2023-01-15"
}
```

**Passo 4: Survival Service processa dados**

```python
        # Calcula dias sobrevividos
        days = calculate_days_survived(character['joined_at'])
        
        # Classifica sobrevivência
        rating = calculate_survival_rating(days)
        
        # Calcula score (0-10)
        score = calculate_survivability_score(
            character['health'],   
            character['hunger'],   
            character['sanity']    
        )
        
        # Avalia riscos
        risks = assess_risks(150, 150, 200)
        
        # Gera recomendações
        recommendations = generate_recommendations(character, risks)
```

#### Funções de Cálculo Detalhadas

**1. Calcular Dias Sobrevividos:**

```python
def calculate_days_survived(joined_at):
    try:
        joined_date = datetime.strptime(joined_at, '%Y-%m-%d')
        today = datetime.now()
        delta = today - joined_date
        return delta.days
    except:
        return 0

```

**2. Classificação de Sobrevivência:**

```python
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

```

**3. Score de Sobrevivência (0-10):**

```python
def calculate_survivability_score(health, hunger, sanity):
    total_stats = health + hunger + sanity
    base_score = total_stats / 50
    return round(min(10.0, base_score), 1)

```

**4. Avaliação de Riscos:**

```python
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
```

**5. Recomendações Personalizadas:**

```python
def generate_recommendations(character, risks):
    recommendations = []
    
    # Baseado em stats
    if character['hunger'] >= 200:
        recommendations.append("High hunger, can sustain long expeditions")
    
    if character['sanity'] < 120:
        recommendations.append("Craft Sanity-restoring items (Jerky, Cooked Green Cap, Taffy)")
    
    # Específico do personagem
    if character['name'] == "Wilson":
        recommendations.append("Use Beard for Winter Insulation")
    
    if character['name'] == "WX-78":
        recommendations.append("Seek lightning strikes for stat upgrades")
    
    # Baseado em risco geral
    if risks['overall_risk'] == "Stable":
        recommendations.append("Character is in good condition for exploration")
    elif risks['overall_risk'] == "Critical":
        recommendations.append("Focus on basic survival needs immediately")
    
    return recommendations
```

**Passo 5: Survival Service retorna dados enriquecidos**

```json
{
  "id": 1,
  "name": "Wilson",
  "title": "The Gentleman Scientist",
  "base_stats": {
    "health": 150,
    "hunger": 150,
    "sanity": 200
  },
  "special_ability": "Grows a Magnificent Beard",
  "survival_odds": "Grim",
  "survival_info": {
    "days_survived": 1049,
    "survival_rating": "Master of The Constant",
    "total_stat_points": 500,
    "survivability_score": 10.0,
    "status": "Thriving - 1049 days in The Constant"
  },
  "risk_assessment": {
    "hunger_risk": "Low",
    "sanity_risk": "Very Low",
    "health_risk": "Low",
    "overall_risk": "Stable"
  },
  "recommendations": [
    "Good hunger management",
    "Decent sanity reserves",
    "Standard health capacity",
    "Character is in good condition for exploration"
  ],
  "joined_at": "2023-01-15",
  "fetched_from": "characters-service",
  "calculated_at": "2025-11-29T15:45:30.123456"
}
```

### 3. Resolução DNS e Comunicação de Rede

#### Configuração Docker Compose

```yaml
services:
  characters-service:
    container_name: desafio4-characters
    networks:
      - desafio4-network
    ports:
      - "5001:5001"
  
  survival-service:
    container_name: desafio4-survival
    depends_on:
      - characters-service
    networks:
      - desafio4-network
    ports:
      - "5002:5002"

networks:
  desafio4-network:
    driver: bridge
    name: desafio4-network
```

#### Resolução de Nomes DNS

```
┌────────────────────────────────────────────────┐
│  Rede: desafio4-network (172.21.0.0/16)       │
│                                                │
│  characters-service (172.21.0.2:5001)         │
│       ↑                                        │
│       │ HTTP GET /characters/1                │
│       │                                        │
│  survival-service (172.21.0.3:5002)           │
│                                                │
└────────────────────────────────────────────────┘
```

**Como Docker resolve "characters-service":**

1. Survival Service executa: `requests.get("http://characters-service:5001/characters/1")`
2. Docker DNS interno intercepta a consulta
3. Resolve `characters-service` → IP do container (`172.21.0.2`)
4. Estabelece conexão TCP para `172.21.0.2:5001`
5. Envia requisição HTTP GET
6. Characters Service responde

**Por que usar nome do serviço ao invés de IP?**

```python
# Usando IP (NÃO recomendado)
url = "http://172.21.0.2:5001/characters"

# Usando nome DNS (RECOMENDADO)
url = "http://characters-service:5001/characters"
```

**Vantagens:**
- ✅ **Flexível**: Docker pode mudar IP do container
- ✅ **Legível**: Nome do serviço é mais claro que IP
- ✅ **Portável**: Funciona em qualquer ambiente
- ✅ **Escalável**: Funciona com múltiplas réplicas (load balancing automático)

### 4. Tratamento de Erros e Resiliência

#### Timeout na Requisição

```python
response = requests.get(url, timeout=5)
```

**O que acontece se Characters Service estiver lento?**

```
[Tempo: 0s] Survival Service envia requisição
[Tempo: 1s] Characters Service processando...
[Tempo: 2s] Characters Service processando...
[Tempo: 5s] TIMEOUT! requests.exceptions.Timeout
```

#### Service Unavailable (503)

```python
    except requests.exceptions.RequestException as e:
        log_info(f"[SURVIVAL-STATS] ERRO ao conectar com Characters Service: {str(e)}")
        return jsonify({
            'error': 'Characters Service indisponivel',
            'message': 'Não foi possível obter dados dos personagens',
            'details': str(e)
        }), 503
```

**Cenários de erro tratados:**

1. **ConnectionError**: Characters Service offline
2. **Timeout**: Requisição demorou mais de 5 segundos
3. **404 Not Found**: Personagem não existe
4. **500 Internal Server Error**: Erro no Characters Service

**Resposta de erro:**

```json
{
  "error": "Characters Service indisponivel",
  "message": "Não foi possível obter dados dos personagens",
  "details": "HTTPConnectionPool(host='characters-service', port=5001): Max retries exceeded"
}
```

### 5. Endpoint Agregado: `/server-overview`

**Combina múltiplos personagens em estatísticas:**

```python
@app.route('/server-overview', methods=['GET'])
def server_overview():
    # Busca TODOS os personagens
    response = requests.get(f"{CHARACTERS_SERVICE_URL}/characters")
    characters = response.json()['characters']
    
    # Calcula médias
    total_chars = len(characters)
    avg_health = sum(c['health'] for c in characters) / total_chars
    avg_hunger = sum(c['hunger'] for c in characters) / total_chars
    avg_sanity = sum(c['sanity'] for c in characters) / total_chars
    
    # Distribuição de survival odds
    odds_distribution = {}
    for char in characters:
        odds = char['survival_odds']
        odds_distribution[odds] = odds_distribution.get(odds, 0) + 1
    
    # Total de dias acumulados
    total_days = sum(calculate_days_survived(c['joined_at']) for c in characters)
    
    return jsonify({
        'server_statistics': {
            'total_characters': total_chars,
            'total_days_survived': total_days,
            'average_stats': {
                'health': round(avg_health, 1),
                'hunger': round(avg_hunger, 1),
                'sanity': round(avg_sanity, 1)
            },
            'survival_odds_distribution': odds_distribution
        }
    })
```

**Resposta:**

```json
{
  "server_statistics": {
    "total_characters": 7,
    "total_days_survived": 6876,
    "average_stats": {
      "health": 132.1,
      "hunger": 135.7,
      "sanity": 145.7
    },
    "survival_odds_distribution": {
      "Grim": 5,
      "Slim": 1,
      "None": 1
    },
    "server_status": "Active and Thriving"
  },
  "fetched_from": "characters-service",
  "generated_at": "2025-11-29T15:50:00.123456"
}
```

### 6. Dependências com `depends_on`

```yaml
survival-service:
  depends_on:
    - characters-service
```

**Sequência de inicialização:**

```
1. docker-compose up
2. Cria rede desafio4-network
3. Inicia container characters-service
4. Aguarda characters-service estar "started"
5. Inicia container survival-service
6. Survival Service pode imediatamente chamar Characters Service
```

### 7. Decisões Técnicas

#### Por que JSON file ao invés de banco de dados?

**Characters Service usa JSON:**

```python
def load_characters():
    with open('characters_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)
```

**Vantagens:**
- **Simplicidade**: Não precisa configurar banco de dados
- **Portabilidade**: JSON funciona em qualquer ambiente
- **Foco**: Demonstra comunicação HTTP, não persistência de dados
- **Performance**: Dados em memória são extremamente rápidos

**Desvantagens:**
- Dados resetados ao reiniciar container
- Não escalável para muitos dados
- Sem transações ACID

**Quando usar banco de dados:**
- Dados precisam persistir
- Múltiplas escritas simultâneas
- Volume grande de dados
- Relações complexas entre entidades

#### Por que microsserviços separados ao invés de monolito?

**Monolito (alternativa):**

```python
# Um único serviço com tudo
@app.route('/characters')
def get_characters():
    return characters_db

@app.route('/survival-stats/<id>')
def get_survival_stats(id):
    char = characters_db[id]
    return calculate_stats(char)
```

**Vantagens dos microsserviços:**
- **Separação de responsabilidades**: Characters Service só gerencia personagens
- **Escalabilidade independente**: Pode escalar Survival Service sem afetar Characters
- **Desenvolvimento paralelo**: Times diferentes podem trabalhar em cada serviço
- **Resiliência**: Falha em um serviço não derruba o outro
- **Tecnologias diferentes**: Poderia usar Python no Characters e Node.js no Survival

**Desvantagens:**
- Mais complexo (mais containers, rede, comunicação)
- Latência de rede entre serviços
- Tratamento de erros distribuídos

#### Por que não usar mensageria (RabbitMQ/Kafka)?

**HTTP síncrono (usado):**

```python
response = requests.get(url)  # Aguarda resposta
data = response.json()
```

**Mensageria assíncrona (alternativa):**

```python
# Publica mensagem
publisher.send("character-request", {"id": 1})

# Aguarda resposta em outro canal
@subscriber.on("character-response")
def handle_response(data):
    # Processa dados
```

**Quando usar HTTP:**
- Requisição/resposta imediata
- Mais simples de implementar
- Fácil debug e teste
- Ideal para consultas (read operations)

**Quando usar mensageria:**
- Operações assíncronas (não precisa aguardar)
- Alta throughput (milhares de mensagens/segundo)
- Desacoplamento temporal (serviço pode estar offline temporariamente)
- Event-driven architecture

---

## 🎮 Personagens Disponíveis

| ID | Nome | Título | Health | Hunger | Sanity | Survival Odds |
|----|------|--------|--------|--------|--------|---------------|
| 1 | Wilson | The Gentleman Scientist | 150 | 150 | 200 | Grim |
| 2 | Willow | The Firestarter | 150 | 150 | 120 | Grim |
| 3 | Wormwood | The Lonesome | 150 | 150 | 200 | Grim |
| 4 | WX-78 | The Soulless Automaton | 100 | 100 | 100 | Grim |
| 5 | Wigfrid | The Performance Artist | 200 | 120 | 120 | Slim |
| 6 | Warly | The Culinarian | 150 | 250 | 200 | Grim |
| 7 | Wes | The Silent | 75 | 75 | 75 | None |


## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```bash
   cd desafio4
   ```

2. **Suba os microsserviços:**
   ```bash
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```bash
   docker-compose ps
   ```

## 📊 Endpoints dos Microsserviços

### Microsserviço A: Characters Service

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/characters` | Lista todos os personagens |
| GET | `/characters/<id>` | Detalhes de um personagem |
| GET | `/characters/odds/<level>` | Filtra por survival odds (Slim, Grim, None) |
| POST | `/characters` | Adiciona novo personagem |
| GET | `/health` | Health check |

### Microsserviço B: Survival Stats Service

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações do serviço |
| GET | `/survival-stats` | Stats de todos (consome Serviço A) |
| GET | `/survival-stats/<id>` | Análise detalhada (consome Serviço A) |
| GET | `/server-overview` | Estatísticas agregadas do servidor |
| GET | `/health` | Health check |


## 🧪 Testando os Microsserviços

### Microsserviço A: Characters Service (Port 5001)

#### 1. Informações do serviço
```bash
curl http://localhost:5001/
```

#### 2. Listar todos os personagens
```bash
curl http://localhost:5001/characters
```

**Resposta esperada:**
```json
{
  "total": 7,
  "characters": [
    {
      "id": 1,
      "name": "Wilson",
      "title": "The Gentleman Scientist",
      "health": 150,
      "hunger": 150,
      "sanity": 200,
      "special_ability": "Grows a magnificent beard...",
      "survival_odds": "Grim",
      "joined_at": "2025-06-15"
    }
  ]
}
```

#### 3. Buscar personagem específico
```bash
curl http://localhost:5001/characters/1
```

#### 4. Filtrar por survival odds (Slim, Grim ou None)
```bash
# Slim (melhores chances)
curl http://localhost:5001/characters/odds/Slim

# Grim (chances razoáveis)
curl http://localhost:5001/characters/odds/Grim

# None (praticamente impossível)
curl http://localhost:5001/characters/odds/None
```

#### 5. Adicionar novo personagem via POST
```bash
curl -X POST http://localhost:5001/characters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Woodie",
    "title": "The Lumberjack",
    "health": 150,
    "hunger": 150,
    "sanity": 200,
    "special_ability": "Can transform into a Werebeaver",
    "survival_odds": "Grim",
    "joined_at": "2025-11-19"
  }'
```

**Resposta esperada:**
```json
{
  "message": "Personagem adicionado com sucesso",
  "character": {
    "id": 8,
    "name": "Woodie",
    "title": "The Lumberjack",
    "health": 150,
    "hunger": 150,
    "sanity": 200,
    "special_ability": "Can transform into a Werebeaver",
    "survival_odds": "Grim",
    "joined_at": "2025-11-19"
  }
}
```

### Microsserviço B: Survival Stats Service (Port 5002)

#### 1. Informações do serviço
```bash
curl http://localhost:5002/
```

#### 2. Survival stats de todos os personagens
```bash
curl http://localhost:5002/survival-stats
```

**Resposta esperada:**
```json
{
  "total": 7,
  "survival_stats": [
    {
      "id": 1,
      "name": "Wilson",
      "title": "The Gentleman Scientist",
      "days_survived": 157,
      "survival_rating": "Experienced Survivor",
      "survivability_score": 10.0,
      "status": "Surviving for 157 days in The Constant"
    }
  ],
  "fetched_from": "characters-service"
}
```

#### 3. Análise detalhada de um personagem
```bash
curl http://localhost:5002/survival-stats/1
```

**Resposta enriquecida:**
```json
{
  "id": 1,
  "name": "Wilson",
  "title": "The Gentleman Scientist",
  "base_stats": {
    "health": 150,
    "hunger": 150,
    "sanity": 200
  },
  "survival_info": {
    "days_survived": 157,
    "survival_rating": "Experienced Survivor",
    "survivability_score": 10.0,
    "status": "Thriving - 157 days in The Constant"
  },
  "risk_assessment": {
    "hunger_risk": "Low",
    "sanity_risk": "Very Low",
    "health_risk": "Low",
    "overall_risk": "Stable"
  },
  "recommendations": [
    "Good hunger management",
    "Hight sanity, safe for shadow creature farming",
    "Standard health capacity",
    "Character is in good condition for exploration"
  ],
  "fetched_from": "characters-service"
}
```

#### 4. Visão geral do servidor
```bash
curl http://localhost:5002/server-overview
```



