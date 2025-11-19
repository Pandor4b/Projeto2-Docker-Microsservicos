# Desafio 3 — Docker Compose Orquestrando Serviços

## 📋 Descrição do Projeto

Sistema de batalha Pokémon usando as **8 Eeveelutions** (evoluções do Eevee). Demonstra orquestração de 3 serviços interdependentes: API de batalha, banco de dados PostgreSQL e cache Redis.

**Objetivo:** Demonstrar comunicação e dependências entre múltiplos serviços orquestrados via Docker Compose.

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────┐
│  Battle API (Flask)                         │
│  - Gerencia batalhas                        │
│  - Endpoints HTTP                           │
│  Port: 5000                                 │
└────────┬──────────────────┬─────────────────┘
         │                  │
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  PostgreSQL     │  │  Redis          │
│  - Pokémon data │  │  - Batalhas     │
│  - Histórico    │  │  - Cache        │
└─────────────────┘  └─────────────────┘
```

## 🔧 Tecnologias Utilizadas

- **Docker Compose**: Orquestração
- **Flask**: API REST
- **PostgreSQL 15**: Banco de dados
- **Redis 7**: Cache e sessões
- **Python 3.11**: Linguagem

## 📁 Estrutura do Projeto

```
desafio3/
├── api/
│   ├── app.py              # Battle API
│   ├── Dockerfile
│   └── requirements.txt    # Flask, redis, psycopg2
├── database/
│   └── init.sql            # 8 Eeveelutions + tabelas
├── docker-compose.yml      # Orquestração dos 3 serviços
└── README.md
```

## 🎮 Pokémon Disponíveis

| ID  | Nome     | Tipo     | HP  | Ataque | Defesa | Velocidade |
|-----|----------|----------|-----|--------|--------|------------|
| 134 | Vaporeon | Water    | 130 | 65     | 60     | 65         |
| 135 | Jolteon  | Electric | 65  | 65     | 60     | 130        |
| 136 | Flareon  | Fire     | 65  | 130    | 60     | 65         |
| 196 | Espeon   | Psychic  | 65  | 65     | 60     | 110        |
| 197 | Umbreon  | Dark     | 95  | 65     | 110    | 65         |
| 470 | Leafeon  | Grass    | 65  | 110    | 130    | 95         |
| 471 | Glaceon  | Ice      | 65  | 60     | 110    | 65         |
| 700 | Sylveon  | Fairy    | 95  | 65     | 65     | 60         |


## 📊 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/pokemon` | Lista todos os Pokémon disponíveis |
| GET | `/pokemon/<id>` | Detalhes de um Pokémon específico (com cache Redis) |
| POST | `/battle/start` | Inicia e executa batalha completa automaticamente |
| GET | `/history` | Histórico das últimas 10 batalhas |

### Exemplos de uso:

```powershell
# Listar todos os Pokémon
curl http://localhost:5000/pokemon

# Ver detalhes de um Pokémon (ex: Jolteon)
curl http://localhost:5000/pokemon/135

# Iniciar batalha (Jolteon vs Vaporeon)
curl -X POST http://localhost:5000/battle/start -H "Content-Type: application/json" -d "{\"pokemon1_id\": 135, \"pokemon2_id\": 134}"

# Ver histórico
curl http://localhost:5000/history
```

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```powershell
   cd desafio3
   ```

2. **Suba os 3 serviços:**
   ```powershell
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```powershell
   docker-compose ps
   ```

## 🧪 Testando a Comunicação entre Serviços

### 1. Listar Pokémon

```powershell
curl http://localhost:5000/pokemon
```

**Logs esperados:**
```
[BATTLE-API] Listando Pokémon...
[BATTLE-API] Consultando PostgreSQL...
[BATTLE-API] 8 Pokémon encontrados
```

### 2. Buscar Pokémon Específico 

```powershell
# Primeira consulta (cache miss)
curl http://localhost:5000/pokemon/135

# Segunda consulta (cache hit)
curl http://localhost:5000/pokemon/135
```

**Logs esperados:**
```
# Primeira vez:
[BATTLE-API] Buscando Pokémon ID: 135
[REDIS] Cache MISS para Pokémon 135
[BATTLE-API] Consultando PostgreSQL...
[REDIS] Salvando Pokémon 135 no cache

# Segunda vez:
[BATTLE-API] Buscando Pokémon ID: 135
[REDIS] Cache HIT para Pokémon 135
```

### 3. Iniciar Batalha

```powershell
# Jolteon vs Vaporeon
curl -X POST http://localhost:5000/battle/start -H "Content-Type: application/json" -d "{\"pokemon1_id\": 135, \"pokemon2_id\": 134}"
```

**Output:**
```json
{
  "battle_id": 1,
  "pokemon1": "Jolteon",
  "pokemon2": "Vaporeon",
  "vencedor": "Jolteon",
  "perdedor": "Vaporeon",
  "turnos": 5,
  "log": [
    "Turno 1: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 95/130",
    "Turno 2: Vaporeon ataca Jolteon causando 20 de dano! HP restante: 45/65",
    "Turno 3: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 60/130",
    "Turno 4: Vaporeon ataca Jolteon causando 20 de dano! HP restante: 25/65",
    "Turno 5: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 25/130"
  ],
  "status": "finalizada"
}
```

**Logs esperados:**
```
[BATTLE-API] Iniciando batalha: 135 vs 134
[BATTLE-API] Consultando PostgreSQL para Pokémon 1...
[BATTLE-API] Consultando PostgreSQL para Pokémon 2...
[BATTLE-API] Jolteon (Speed: 130) ataca primeiro!
[BATTLE-API] Turno 1: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 95/130
[BATTLE-API] Turno 2: Vaporeon ataca Jolteon causando 20 de dano! HP restante: 45/65
[BATTLE-API] Turno 3: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 60/130
[BATTLE-API] Turno 4: Vaporeon ataca Jolteon causando 20 de dano! HP restante: 25/65
[BATTLE-API] Turno 5: Jolteon ataca Vaporeon causando 35 de dano! HP restante: 25/130
[BATTLE-API] Jolteon venceu após 5 turnos!
[BATTLE-API] Salvando resultado no PostgreSQL...
[POSTGRES] Batalha salva no histórico
```

### 4. Ver Histórico

```powershell
curl http://localhost:5000/history
```

**Output:**
```json
[
  {
    "id": 1,
    "pokemon1": "Jolteon",
    "pokemon2": "Vaporeon",
    "vencedor": "Jolteon",
    "turnos": 5,
    "data": "2025-11-18 15:30:45"
  }
]
```



## 🔍 Verificando Dependências

### Ver logs de todos os serviços:
```powershell
docker-compose logs -f
```

### Ver logs específicos:
```powershell
# API
docker logs desafio3-battle-api

# PostgreSQL
docker logs desafio3-postgres

# Redis
docker logs desafio3-redis
```

### Acessar PostgreSQL diretamente:
```powershell
docker exec -it desafio3-postgres psql -U trainer -d pokemon_db

# Comandos SQL:
SELECT * FROM pokemon;
SELECT * FROM batalhas;
\q
```

### Acessar Redis diretamente:
```powershell
docker exec -it desafio3-redis redis-cli

# Comandos Redis:
KEYS *
GET pokemon:135
GET battle:*
```

## 📊 Comandos Úteis

```powershell
# Iniciar
docker-compose up -d

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Limpar tudo
docker-compose down -v --rmi all
```