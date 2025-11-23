# Desafio 4 — Microsserviços Independentes

## 📋 Descrição do Projeto

Sistema de gerenciamento de personagens e análise de sobrevivência para **Don't Starve Together**. Demonstra comunicação HTTP entre dois microsserviços independentes.

**Objetivo:** Criar arquitetura de microsserviços onde um serviço consome dados de outro via HTTP.

---

## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🎮 Personagens](#-personagens-disponíveis) • [🚀 Executar](#-como-executar) • [📊 Endpoints](#-endpoints-dos-microsserviços) • [🧪 Testes](#-testando-os-microsserviços)

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

- **Docker**: Containerização dos microsserviços
- **Flask**: Framework web para ambos os serviços
- **Python 3.11**: Linguagem de programação
- **Requests**: Biblioteca para comunicação HTTP entre serviços

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



## Visualizando logs da comunicação:

```bash
# Terminal 1: Logs do Characters Service
docker logs -f desafio4-characters-service

# Terminal 2: Logs do Survival Stats Service
docker logs -f desafio4-survival-service
```