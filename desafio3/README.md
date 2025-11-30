# Desafio 3 — Docker Compose Orquestrando Serviços

## 📋 Descrição do Projeto

Sistema de batalha Pokémon usando as **8 Eeveelutions** (evoluções do Eevee). Demonstra orquestração de 3 serviços interdependentes: API de batalha, banco de dados PostgreSQL e cache Redis.


---

## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🔍 Como Funciona](#-como-funciona) • [🎮 Pokémon](#-pokémon-disponíveis) • [🚀 Executar](#-como-executar) • [📊 Endpoints](#-endpoints-da-api) • [🧪 Testes](#-testando-a-comunicação-entre-serviços)

---

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

- **Docker**: Containerização, orquestração e redes
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web para API REST
- **PostgreSQL 15**: Banco de dados relacional
- **Redis 7**: Cache em memória
- **psycopg2**: Driver PostgreSQL para Python

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

## 🔍 Como Funciona

### 1. Arquitetura de Três Camadas

#### Camada 1: PostgreSQL (Persistência)

**Responsabilidade:** Armazenar dados permanentes

```yaml
db:
  image: postgres:15-alpine
  volumes:
    - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
```

**Tabelas criadas:**

```sql
-- Tabela de Pokémon (8 Eeveelutions)
CREATE TABLE pokemon (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50),
    tipo VARCHAR(20),
    hp INTEGER,
    ataque INTEGER,
    defesa INTEGER,
    ataque_especial INTEGER,
    defesa_especial INTEGER,
    velocidade INTEGER
);

-- Tabela de histórico de batalhas
CREATE TABLE batalhas (
    id SERIAL PRIMARY KEY,
    pokemon1_id INTEGER,
    pokemon1_nome VARCHAR(50),
    pokemon2_id INTEGER,
    pokemon2_nome VARCHAR(50),
    vencedor_id INTEGER,
    vencedor_nome VARCHAR(50),
    turnos INTEGER,
    data_batalha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Dados iniciais:**
- 8 Pokémon (Vaporeon, Jolteon, Flareon, Espeon, Umbreon, Leafeon, Glaceon, Sylveon)
- Cada um com stats únicos (HP, Ataque, Defesa, etc.)

#### Camada 2: Redis (Cache)

**Responsabilidade:** Cache de consultas frequentes

```yaml
cache:
  image: redis:7-alpine
  networks:
    - desafio3-network
```

**Funcionamento do cache:**

1. **Cache Key**: `pokemon:{id}`
2. **TTL (Time To Live)**: 300 segundos (5 minutos)
3. **Formato**: JSON string

```python
# Salvando no cache
redis_client.setex(
    f"pokemon:{pokemon_id}",  # Chave
    300,                       # TTL em segundos
    json.dumps(pokemon)        # Valor serializado
)

# Lendo do cache
cached = redis_client.get(f"pokemon:{pokemon_id}")
if cached:
    return json.loads(cached)  # Cache HIT
else:
    # Cache MISS → consulta PostgreSQL
```

**Por que usar cache?**
- ✅ **Performance**: Redis é ~100x mais rápido que PostgreSQL para leitura
- ✅ **Reduz carga**: Menos queries no banco de dados
- ✅ **Escalabilidade**: Suporta milhares de requisições/segundo

#### Camada 3: Battle API (Lógica de Negócio)

**Responsabilidade:** Orquestrar batalhas e gerenciar comunicação

```yaml
api:
  depends_on:
    - db      # Aguarda PostgreSQL
    - cache   # Aguarda Redis
  environment:
    - DB_HOST=db
    - REDIS_HOST=cache
```

**Conexões:**

```python
# PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'pokemon_db'),
    'user': os.getenv('DB_USER', 'trainer'),
    'password': os.getenv('DB_PASSWORD', 'pokeball')
}

# Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'cache'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True  # Retorna strings ao invés de bytes
)
```

### 2. Fluxo de uma Batalha Completa

#### Passo 1: Cliente inicia batalha

```bash
curl -X POST http://localhost:5000/battle/start \
  -H "Content-Type: application/json" \
  -d '{"pokemon1_id": 135, "pokemon2_id": 134}'
```

#### Passo 2: API consulta dados dos Pokémon

```python
@app.route('/battle/start', methods=['POST'])
def iniciar_batalha():
    pokemon1_id = data.get('pokemon1_id')  # 135 (Jolteon)
    pokemon2_id = data.get('pokemon2_id')  # 134 (Vaporeon)
    
    # Consulta PostgreSQL (não usa cache para garantir dados frescos)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pokemon WHERE id = %s", (pokemon1_id,))
    p1 = cursor.fetchone()  # (135, 'Jolteon', 'Electric', 65, 65, 60, 110, 95, 130)
    
    cursor.execute("SELECT * FROM pokemon WHERE id = %s", (pokemon2_id,))
    p2 = cursor.fetchone()  # (134, 'Vaporeon', 'Water', 130, 65, 60, 110, 95, 65)
```

**Estrutura dos dados:**

```python
pokemon1 = {
    'id': 135,
    'nome': 'Jolteon',
    'tipo': 'Electric',
    'hp_atual': 65,
    'hp_max': 65,
    'ataque': 65,
    'defesa': 60,
    'ataque_especial': 110,
    'defesa_especial': 95,
    'velocidade': 130  # Jolteon é mais rápido!
}
```

#### Passo 3: Determina quem ataca primeiro

```python
if pokemon1['velocidade'] >= pokemon2['velocidade']:
    atacante = pokemon1  # Jolteon (130 Speed)
    defensor = pokemon2   # Vaporeon (65 Speed)
else:
    atacante = pokemon2
    defensor = pokemon1

# Resultado: Jolteon ataca primeiro!
```

#### Passo 4: Loop de batalha

```python
turno = 0
log_batalha = []

while pokemon1['hp_atual'] > 0 and pokemon2['hp_atual'] > 0:
    turno += 1
    
    # Calcula dano
    dano = calcular_dano(atacante, defensor)
    defensor['hp_atual'] = max(0, defensor['hp_atual'] - dano)
    
    # Log do turno
    log_entry = f"Turno {turno}: {atacante['nome']} ataca {defensor['nome']} causando {dano} de dano!"
    log_batalha.append(log_entry)
    
    # Verifica se defensor foi derrotado
    if defensor['hp_atual'] <= 0:
        vencedor = atacante
        perdedor = defensor
        break
    
    # Troca atacante e defensor
    atacante, defensor = defensor, atacante
```

**Exemplo de execução:**

```
Turno 1: Jolteon ataca Vaporeon causando 63 de dano! HP: 67/130
Turno 2: Vaporeon ataca Jolteon causando 35 de dano! HP: 30/65
Turno 3: Jolteon ataca Vaporeon causando 63 de dano! HP: 4/130
Turno 4: Vaporeon ataca Jolteon causando 35 de dano! HP: 0/65 
Vencedor: Vaporeon!
```

#### Passo 5: Cálculo de dano

```python
def calcular_dano(atacante, defensor):
    # Usa o maior stat de ataque (físico ou especial)
    atk = max(atacante['ataque'], atacante['ataque_especial'])
    
    # Usa o maior stat de defesa (físico ou especial)
    defe = max(defensor['defesa'], defensor['defesa_especial'])
    
    # Fórmula simplificada de dano
    dano = max(5, int((atk * 2) / (defe * 0.5)))
    
    return dano
```

**Exemplo: Jolteon vs Vaporeon (Turno 1)**

```python
# Jolteon atacando
atk = max(65, 110) = 110  # Ataque Especial é maior
defe = max(60, 95) = 95   # Defesa Especial de Vaporeon

dano = max(5, int((110 * 2) / (95 * 0.5)))
     = max(5, int(220 / 47.5))
     = max(5, 4)
     = 5  # Dano mínimo

# Vaporeon contra-atacando
atk = max(65, 110) = 110  # Ataque Especial de Vaporeon
defe = max(60, 95) = 95   # Defesa Especial de Jolteon

dano = max(5, int((110 * 2) / (95 * 0.5)))
     = 5
```

#### Passo 6: Salva resultado no PostgreSQL

```python
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
```

**Dados salvos:**

```
battle_id: 1
pokemon1: Jolteon (ID: 135)
pokemon2: Vaporeon (ID: 134)
vencedor: Vaporeon (ID: 134)
turnos: 4
data_batalha: 2025-11-29 15:30:45
```

#### Passo 7: Retorna resultado

```json
{
  "battle_id": 1,
  "pokemon1": "Jolteon",
  "pokemon2": "Vaporeon",
  "vencedor": "Vaporeon",
  "perdedor": "Jolteon",
  "turnos": 4,
  "log": [
    "Turno 1: Jolteon ataca Vaporeon causando 63 de dano! HP: 67/130",
    "Turno 2: Vaporeon ataca Jolteon causando 35 de dano! HP: 30/65",
    "Turno 3: Jolteon ataca Vaporeon causando 63 de dano! HP: 4/130",
    "Turno 4: Vaporeon ataca Jolteon causando 35 de dano! HP: 0/65"
  ],
  "status": "finalizada"
}
```

### 3. Endpoint `/pokemon/<id>` com Cache

#### Primeira consulta (Cache MISS)

```
Cliente: GET /pokemon/135
    ↓
API: Verifica Redis para "pokemon:135"
    ↓
Redis: Chave não existe (MISS)
    ↓
API: Consulta PostgreSQL
    ↓
PostgreSQL: SELECT * FROM pokemon WHERE id = 135
    ↓
API: Recebe dados de Jolteon
    ↓
API: Salva no Redis com TTL de 300s
    ↓
Redis: SET pokemon:135 {"id":135,"nome":"Jolteon",...} EX 300
    ↓
API: Retorna JSON para cliente
```

**Log:**
```
[BATTLE-API] Buscando Pokemon ID: 135
[REDIS] Cache MISS para Pokemon 135
[BATTLE-API] Consultando PostgreSQL...
[REDIS] Salvando Pokemon 135 no cache
```

#### Segunda consulta (Cache HIT)

```
Cliente: GET /pokemon/135
    ↓
API: Verifica Redis para "pokemon:135"
    ↓
Redis: Chave existe! (HIT)
    ↓
API: Retorna direto do Redis (sem consultar PostgreSQL)
    ↓
Cliente: Recebe resposta (muito mais rápido!)
```

**Log:**
```
[BATTLE-API] Buscando Pokemon ID: 135
[REDIS] Cache HIT para Pokemon 135
```

**Diferença de performance:**
- PostgreSQL: ~50-100ms
- Redis: ~1-5ms
- **Ganho: 10-20x mais rápido!**

#### Expiração do Cache (após 5 minutos)

```
[Tempo: 0s] GET /pokemon/135 → Cache MISS → Salva no Redis
[Tempo: 10s] GET /pokemon/135 → Cache HIT (289s restantes)
[Tempo: 150s] GET /pokemon/135 → Cache HIT (149s restantes)
[Tempo: 301s] GET /pokemon/135 → Cache MISS (expirou!) → Salva novamente
```

### 4. Comunicação entre Serviços

#### Rede Docker Interna

```yaml
networks:
  desafio3-network:
    driver: bridge
    name: desafio3-network
```

**Topologia:**

```
┌──────────────────────────────────────────────┐
│  Rede: desafio3-network (172.20.0.0/16)     │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │  api (172.20.0.4:5000)              │    │
│  │  - Exposto: localhost:5000          │    │
│  └────────┬──────────────┬─────────────┘    │
│           │              │                   │
│           │              │                   │
│  ┌────────▼────────┐  ┌──▼──────────────┐  │
│  │  db             │  │  cache           │  │
│  │  172.20.0.2     │  │  172.20.0.3      │  │
│  │  postgres:5432  │  │  redis:6379      │  │
│  │  (interno)      │  │  (interno)       │  │
│  └─────────────────┘  └──────────────────┘  │
│                                              │
└──────────────────────────────────────────────┘
```

**Resolução de nomes:**

```python

# PostgreSQL
conn = psycopg2.connect(host='db', ...)

# Redis
redis_client = redis.Redis(host='cache', ...)
```

#### Dependências com `depends_on`

```yaml
api:
  depends_on:
    - db
    - cache
```

**Sequência de inicialização:**

```
1. docker-compose up
2. Cria rede desafio3-network
3. Inicia container "db" (PostgreSQL)
4. Inicia container "cache" (Redis)
5. Aguarda ambos estarem "started"
6. Inicia container "api" (Flask)
7. API tenta conectar aos serviços
```

**Limitação do `depends_on`:**
- Garante apenas que containers **iniciaram**
- Não garante que serviços estão **prontos**
- API precisa implementar retry (não implementado neste projeto)

### 5. Variáveis de Ambiente

```yaml
api:
  environment:
    - DB_HOST=db
    - DB_NAME=pokemon_db
    - DB_USER=trainer
    - DB_PASSWORD=pokeball
    - REDIS_HOST=cache
    - REDIS_PORT=6379
```

**No código Python:**

```python
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),  # Usa 'db' se variável não existir
    'database': os.getenv('DB_NAME', 'pokemon_db'),
    'user': os.getenv('DB_USER', 'trainer'),
    'password': os.getenv('DB_PASSWORD', 'pokeball')
}

REDIS_HOST = os.getenv('REDIS_HOST', 'cache')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
```

**Por que usar variáveis de ambiente?**
- **Flexibilidade**: Mudar configuração sem alterar código
- **Segurança**: Não expor credenciais no código-fonte
- **Portabilidade**: Funciona em qualquer ambiente (dev/prod)

### 6. Decisões Técnicas

#### Por que Redis ao invés de cache in-memory (dict)?

```python
# Cache in-memory (alternativa simples)
cache = {}
cache[f"pokemon:{id}"] = pokemon

# Redis (usado no projeto)
redis_client.setex(f"pokemon:{id}", 300, json.dumps(pokemon))
```

**Vantagens do Redis:**
- Persistente (sobrevive a reinicializações)
- Compartilhado entre múltiplas instâncias da API
- TTL automático (expira dados antigos)
- Mais realista para produção

**Desvantagens:**
- Complexidade adicional (mais um serviço)
- Requer serialização/desserialização JSON


---

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

