# Desafio 5 — Microsserviços com API Gateway

## 📋 Descrição do Projeto

Sistema de **Locadora de Discos de Vinil** implementando o padrão **API Gateway** para centralizar o acesso a dois microsserviços independentes.


## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🔍 Como Funciona](#-como-funciona) • [💿 Dados do Sistema](#-dados-do-sistema) • [🚀 Executar](#-como-executar) • [📊 Endpoints](#-endpoints-do-gateway) • [🧪 Testes](#-testando-o-api-gateway)

## 🏗️ Arquitetura da Solução

```
┌──────────────────────────────────────────────────────────────────┐
│              ARQUITETURA COM API GATEWAY                         │
│              Vinyl Records Rental Shop                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                     CLIENTE EXTERNO                              │
│                           │                                      │
│                           ↓                                      │
│              ┌────────────────────────┐                         │
│              │     API GATEWAY        │  ← Ponto único          │
│              │     (Port 8080)        │    de entrada           │
│              │   [EXPOSTO]            │                         │
│              └─────────┬──────────────┘                         │
│                        │                                         │
│        ┌───────────────┴───────────────┐                        │
│        ↓                               ↓                        │
│  ┌──────────────┐              ┌──────────────┐               │
│  │   Records    │              │   Rentals    │               │
│  │   Service    │              │   Service    │               │
│  │ (Port 5001)  │              │ (Port 5002)  │               │
│  │ [INTERNO]    │              │ [INTERNO]    │               │
│  └──────────────┘              └──────────────┘               │
│                                                                  │
│  Catálogo de vinis              Clientes e aluguéis            │
│  Controle de estoque            Histórico e devoluções         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 🔧 Tecnologias Utilizadas

- **Docker**: Containerização, orquestração e redes
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web para APIs REST
- **Requests**: Biblioteca HTTP para comunicação entre serviços
- **API Gateway Pattern**: Padrão arquitetural de microsserviços

## 📁 Estrutura do Projeto

```
desafio5/
├── gateway/                     # API Gateway (Ponto único de entrada)
│   ├── app.py                   # Roteamento e orquestração
│   ├── Dockerfile
│   └── requirements.txt
├── records-service/             # Microsserviço 1 - Catálogo
│   ├── app.py                   # API REST de discos
│   ├── records_data.json        # 10 vinis clássicos
│   ├── Dockerfile
│   └── requirements.txt
├── rentals-service/             # Microsserviço 2 - Aluguéis
│   ├── app.py                   # API REST de aluguéis
│   ├── customers_data.json      # 5 clientes cadastrados
│   ├── rentals_data.json        # Histórico de aluguéis
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml           # Orquestração dos 3 serviços
└── README.md
```

## 🔍 Como Funciona

### 1. Padrão API Gateway - Arquitetura

#### O Problema: Acesso Direto aos Microsserviços

**Sem API Gateway:**

```
Cliente → http://records-service:5001/records
Cliente → http://rentals-service:5002/rentals
Cliente → http://rentals-service:5002/customers
```

**Desvantagens:**
- Cliente precisa conhecer **múltiplos endpoints**
- Sem ponto centralizado para **autenticação/autorização**
- Difícil implementar **rate limiting** e **logs centralizados**
- Mudanças em microsserviços afetam **todos os clientes**
- Microsserviços **expostos diretamente** ao mundo externo
- Cliente precisa fazer **múltiplas requisições** para obter dados relacionados

#### A Solução: API Gateway Centralizado

**Com API Gateway:**

```
Cliente → http://gateway:8080/records      → Gateway → records-service:5001
Cliente → http://gateway:8080/rentals      → Gateway → rentals-service:5002
Cliente → http://gateway:8080/customers    → Gateway → rentals-service:5002
```

**Vantagens:**
- **Ponto único de entrada**: Cliente conhece apenas o Gateway
- **Roteamento centralizado**: Gateway distribui requisições
- **Agregação de dados**: Gateway combina dados de múltiplos serviços
- **Segurança**: Microsserviços ficam em rede interna
- **Orquestração**: Gateway coordena operações complexas
- **Abstração**: Gateway oculta complexidade dos microsserviços

### 2. Configuração de Rede Docker

```yaml
networks:
  desafio5-network:
    driver: bridge
    name: desafio5-network

services:
  gateway:
    ports:
      - "8080:8080"  # EXPOSTO ao host
    networks:
      - desafio5-network
  
  records-service:
    # SEM mapeamento de portas (interno)
    networks:
      - desafio5-network
  
  rentals-service:
    # SEM mapeamento de portas (interno)
    networks:
      - desafio5-network
```

**Topologia da rede:**

```
┌──────────────────────────────────────────────────┐
│  Host (seu computador)                           │
│                                                  │
│  Acesso: http://localhost:8080                  │
│                ↓                                 │
└────────────────┼─────────────────────────────────┘
                 │ Mapeamento de porta 8080:8080
                 ↓
┌──────────────────────────────────────────────────┐
│  Rede: desafio5-network (172.22.0.0/16)         │
│                                                  │
│  ┌────────────────────────────────────────┐     │
│  │  Gateway (172.22.0.4:8080)             │     │
│  │  - ÚNICO serviço exposto               │     │
│  └────────┬──────────────┬────────────────┘     │
│           │              │                       │
│           │              │                       │
│  ┌────────▼────────┐  ┌──▼──────────────────┐  │
│  │  records-service│  │  rentals-service     │  │
│  │  172.22.0.2     │  │  172.22.0.3          │  │
│  │  :5001 (interno)│  │  :5002 (interno)     │  │
│  │  Não exposto    │  │  Não exposto         │  │
│  └─────────────────┘  └──────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Por que microsserviços não são expostos?**
- **Segurança**: Só o Gateway é acessível externamente
- **Controle**: Todo tráfego passa por um ponto auditável
- **Flexibilidade**: Pode mudar portas internas sem afetar clientes

### 3. Tipos de Endpoints do Gateway

#### Tipo 1: Roteamento Simples (Proxy)

**Cliente → Gateway → Microsserviço**

```python
@app.route('/records', methods=['GET'])
def list_records():
    log_info("[GATEWAY] Buscando catálogo de discos...")
    
    try:
        # Apenas repassa a requisição
        response = requests.get(f"{RECORDS_SERVICE_URL}/records", timeout=5)
        response.raise_for_status()
        
        # Retorna a resposta diretamente
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Serviço de discos está indisponível'}), 503
```

**Fluxo:**

```
Cliente: GET /records
    ↓
Gateway: GET http://records-service:5001/records
    ↓
Records Service: Retorna lista de discos
    ↓
Gateway: Retorna mesma resposta ao cliente
```

**Endpoints deste tipo:**
- `/records` → Lista todos os discos
- `/records/<id>` → Detalhes de um disco
- `/records/genre/<genre>` → Filtra por gênero
- `/customers` → Lista clientes
- `/rentals` → Lista aluguéis

#### Tipo 2: Agregação de Dados

**Cliente → Gateway → Múltiplos Microsserviços → Combina Dados**

```python
@app.route('/records/<int:record_id>/availability', methods=['GET'])
def get_record_availability(record_id):
    try:
        # Busca informações do disco
        log_info(f"[GATEWAY] → GET {RECORDS_SERVICE_URL}/records/{record_id}")
        record_response = requests.get(
            f"{RECORDS_SERVICE_URL}/records/{record_id}", 
            timeout=5
        )
        record = record_response.json()
        
        # Busca aluguéis ativos
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/rentals/active")
        rentals_response = requests.get(
            f"{RENTALS_SERVICE_URL}/rentals/active", 
            timeout=5
        )
        active_rentals = rentals_response.json()['rentals']
        
        # Combina dados: quem está alugando este disco?
        currently_rented_by = [
            r['customer_name'] for r in active_rentals 
            if r['record_id'] == record_id
        ]
        
        # Calcula próxima disponibilidade
        next_available = None
        if record['available_copies'] == 0:
            due_dates = [
                r['due_date'] for r in active_rentals 
                if r['record_id'] == record_id
            ]
            if due_dates:
                next_available = min(due_dates)
        
        # Retorna dados agregados
        return jsonify({
            'record': {
                'id': record['id'],
                'title': record['title'],
                'artist': record['artist']
            },
            'availability': {
                'available_copies': record['available_copies'],
                'is_available': record['available_copies'] > 0,
                'currently_rented_by': currently_rented_by,
                'next_available': next_available
            }
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Erro ao agregar dados'}), 503
```

**Fluxo detalhado:**

```
Cliente: GET /records/7/availability
    ↓
Gateway: 
    ├─> GET records-service:5001/records/7
    │   Resposta: {"id": 7, "title": "The Rise and Fall of a Midwest Princess",
    │              "available_copies": 0, "total_copies": 2}
    │
    └─> GET rentals-service:5002/rentals/active
        Resposta: {"rentals": [
          {"record_id": 7, "customer_name": "Taylor Swift", "due_date": "2025-12-05"},
          {"record_id": 7, "customer_name": "Hayley Williams", "due_date": "2025-12-03"}
        ]}
    ↓
Gateway processa:
    - Filtra aluguéis do disco 7
    - Identifica quem está alugando: ["Taylor Swift", "Hayley Williams"]
    - Calcula próxima devolução: min(["2025-12-05", "2025-12-03"]) = "2025-12-03"
    ↓
Gateway retorna:
{
  "record": {"id": 7, "title": "The Rise and Fall of a Midwest Princess", ...},
  "availability": {
    "available_copies": 0,
    "is_available": false,
    "currently_rented_by": ["Taylor Swift", "Hayley Williams"],
    "next_available": "2025-12-03"
  }
}
```

**Por que isso é poderoso?**
- Cliente faz **1 requisição** ao invés de 2
- Lógica de agregação **centralizada** no Gateway
- Microsserviços permanecem **simples** e focados

#### Tipo 3: Orquestração de Operações (Transações Distribuídas)

**Cliente → Gateway → Múltiplos Microsserviços (Sequencial)**

```python
@app.route('/rent', methods=['POST'])
def create_rental():
    data = request.get_json()  # {"customer_id": 1, "record_id": 7, "rental_days": 3}
    
    try:
        # Valida se disco existe e está disponível
        log_info(f"[GATEWAY] → GET {RECORDS_SERVICE_URL}/records/{data['record_id']}")
        record_response = requests.get(
            f"{RECORDS_SERVICE_URL}/records/{data['record_id']}", 
            timeout=5
        )
        
        if record_response.status_code == 404:
            return jsonify({'error': 'Disco não encontrado'}), 404
        
        record = record_response.json()
        
        if record['available_copies'] <= 0:
            return jsonify({
                'error': 'Disco indisponível',
                'record': record['title']
            }), 400
        
        # Valida se cliente existe
        log_info(f"[GATEWAY] → GET {RENTALS_SERVICE_URL}/customers/{data['customer_id']}")
        customer_response = requests.get(
            f"{RENTALS_SERVICE_URL}/customers/{data['customer_id']}", 
            timeout=5
        )
        
        if customer_response.status_code == 404:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        customer = customer_response.json()
        
        log_info(f"[GATEWAY] Validações OK! Cliente: {customer['name']}, Disco: {record['title']}")
        
        # Cria aluguel
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
            return jsonify(rental_response.json()), rental_response.status_code
        
        rental_result = rental_response.json()
        
        # Decrementa estoque
        log_info(f"[GATEWAY] → PUT {RECORDS_SERVICE_URL}/records/{data['record_id']}/decrease")
        decrease_response = requests.put(
            f"{RECORDS_SERVICE_URL}/records/{data['record_id']}/decrease",
            timeout=5
        )
        decrease_response.raise_for_status()
        
        log_info("[GATEWAY] Aluguel concluído!")
        
        return jsonify({
            'message': 'Aluguel realizado com sucesso',
            'rental': rental_result['rental'],
            'orchestrated_by': 'gateway'
        }), 201
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Falha ao processar aluguel'}), 503
```

**Fluxo completo de orquestração:**

```
Cliente: POST /rent
Body: {"customer_id": 1, "record_id": 7, "rental_days": 3}
    ↓
┌────────────────────────────────────────────────────────┐
│ Gateway orquestra 4 operações sequenciais:            │
├────────────────────────────────────────────────────────┤
│                                                        │
│    GET records-service/records/7                      │
│    Valida: Disco existe? Tem cópias disponíveis?     │
│    Resposta: {"id": 7, "available_copies": 2}        │
│        OK                                               │
│                                                        │
│    GET rentals-service/customers/1                    │
│    Valida: Cliente existe?                            │
│    Resposta: {"id": 1, "name": "Taylor Swift"}       │
│        OK                                               │
│                                                        │
│    POST rentals-service/rentals                       │
│    Cria registro de aluguel                           │
│    Resposta: {"rental": {"id": 10, ...}}             │
│        Aluguel #10 criado                               │
│                                                        │
│    PUT records-service/records/7/decrease             │
│    Atualiza estoque: 2 → 1 cópia disponível          │
│    Resposta: {"available_copies": 1}                  │
│        Estoque atualizado                               │
│                                                        │
└────────────────────────────────────────────────────────┘
    ↓
Gateway retorna:
{
  "message": "Aluguel realizado com sucesso",
  "rental": {"id": 10, "customer_name": "Taylor Swift", ...},
  "orchestrated_by": "gateway"
}
```

**Por que Gateway orquestra ao invés dos microsserviços?**

**Alternativa: Records Service chama Rentals Service diretamente**

```python
# Dentro do Records Service (NÃO RECOMENDADO)
@app.route('/rent', methods=['POST'])
def rent_record():
    # Records Service chamando Rentals Service
    response = requests.post('http://rentals-service:5002/rentals', ...)
    # Cria acoplamento entre microsserviços!
```

**Problemas:**
- **Acoplamento**: Records Service depende de Rentals Service
- **Responsabilidade errada**: Records Service só deveria gerenciar catálogo
- **Difícil manter**: Lógica de negócio espalhada
- **Cascata de falhas**: Se Rentals cai, Records também falha

**Com Gateway:**
- **Desacoplamento**: Microsserviços não se conhecem
- **Single Responsibility**: Cada serviço tem uma responsabilidade
- **Lógica centralizada**: Gateway coordena operações complexas
- **Resiliência**: Falha isolada não afeta outros serviços

#### Tipo 4: Orquestração de Devolução

```python
@app.route('/return/<int:rental_id>', methods=['PUT'])
def return_rental(rental_id):
    try:
        # Busca dados do aluguel
        rental_response = requests.get(
            f"{RENTALS_SERVICE_URL}/rentals/{rental_id}"
        )
        rental = rental_response.json()
        
        if rental['status'] == 'returned':
            return jsonify({'error': 'Aluguel já foi devolvido'}), 400
        
        # Marca como devolvido no Rentals Service
        return_response = requests.put(
            f"{RENTALS_SERVICE_URL}/rentals/{rental_id}/return"
        )
        return_result = return_response.json()
        
        # Incrementa estoque no Records Service
        increase_response = requests.put(
            f"{RECORDS_SERVICE_URL}/records/{rental['record_id']}/increase"
        )
        
        log_info(f"[GATEWAY] '{rental['record_title']}' devolvido ao estoque")
        
        return jsonify({
            'message': 'Devolução processada com sucesso',
            'rental': return_result['rental'],
            'late_fee': return_result['late_fee']
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Falha ao processar devolução'}), 503
```

**Fluxo:**

```
Cliente: PUT /return/10
    ↓
Gateway:
    GET rentals-service/rentals/10
       → Valida: Aluguel existe? Já foi devolvido?
    
    PUT rentals-service/rentals/10/return
       → Marca status: active → returned
       → Calcula multa por atraso (se houver)
    
    PUT records-service/records/7/increase
       → Incrementa estoque: 1 → 2 cópias disponíveis
    ↓
Retorna: {"message": "Devolução processada", "late_fee": 0}
```


### 4. Recomendações Inteligentes

```python
@app.route('/recommendations/<int:customer_id>', methods=['GET'])
def get_recommendations(customer_id):
    try:
        # Busca gênero favorito do cliente
        customer_response = requests.get(
            f"{RENTALS_SERVICE_URL}/customers/{customer_id}"
        )
        customer = customer_response.json()
        favorite_genre = customer['favorite_genre']
        
        # Busca discos do gênero favorito
        records_response = requests.get(
            f"{RECORDS_SERVICE_URL}/records/genre/{favorite_genre}"
        )
        genre_records = records_response.json()['records']
        
        # Filtra apenas disponíveis
        available_recommendations = [
            r for r in genre_records 
            if r['available_copies'] > 0
        ]
        
        return jsonify({
            'customer': {'name': customer['name'], 'favorite_genre': favorite_genre},
            'recommendations': available_recommendations[:5],  # Top 5
            'total_available': len(available_recommendations)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Falha ao gerar recomendações'}), 503
```

**Exemplo:**

```
Cliente: GET /recommendations/1
    ↓
Gateway:
    GET rentals-service/customers/1
       Resposta: {"name": "Taylor Swift", "favorite_genre": "Pop Rock"}
    
    GET records-service/records/genre/Pop Rock
       Resposta: 3 discos de Pop Rock
    
    Filtra apenas disponíveis (available_copies > 0)
       Resultado: 2 discos disponíveis
    ↓
Retorna:
{
  "customer": {"name": "Taylor Swift", "favorite_genre": "Pop Rock"},
  "recommendations": [
    {"id": 1, "title": "After Laughter", "available_copies": 2},
    {"id": 4, "title": "One More Light", "available_copies": 2}
  ],
  "total_available": 2
}
```

### 5. Health Check Agregado

```python
@app.route('/health')
def health():
    services_health = {}
    
    # Verifica Records Service
    try:
        response = requests.get(f"{RECORDS_SERVICE_URL}/health", timeout=2)
        services_health['records_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_health['records_service'] = 'unavailable'
    
    # Verifica Rentals Service
    try:
        response = requests.get(f"{RENTALS_SERVICE_URL}/health", timeout=2)
        services_health['rentals_service'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        services_health['rentals_service'] = 'unavailable'
    
    # Gateway está healthy se TODOS os serviços estão healthy
    all_healthy = all(status == 'healthy' for status in services_health.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'gateway': 'healthy',
        'services': services_health
    })
```

**Possíveis respostas:**

```json
// Tudo funcionando
{
  "status": "healthy",
  "gateway": "healthy",
  "services": {
    "records_service": "healthy",
    "rentals_service": "healthy"
  }
}

// Um serviço com problema
{
  "status": "degraded",
  "gateway": "healthy",
  "services": {
    "records_service": "healthy",
    "rentals_service": "unavailable"
  }
}
```

### 6. Decisões Técnicas

#### Por que API Gateway Pattern?

**Sem Gateway (Microsserviços expostos diretamente):**

```
Cliente ┬─> records-service:5001/records
        └─> rentals-service:5002/rentals

// Cliente precisa:
records = fetch('http://records-service:5001/records/7')
rentals = fetch('http://rentals-service:5002/rentals/active')
// Combinar dados no cliente
```

**Problemas:**
- Cliente conhece **estrutura interna** da arquitetura
- **Múltiplas requisições** (latência acumulada)
- **Sem ponto central** para autenticação/logs
- Microsserviços **expostos** ao mundo externo

**Com Gateway:**

```
Cliente ──> gateway:8080/records/7/availability

// Gateway faz internamente:
- Busca disco no Records Service
- Busca aluguéis no Rentals Service
- Combina e retorna
```

**Vantagens:**
- **Abstração**: Cliente não conhece microsserviços internos
- **1 requisição**: Gateway agrega dados
- **Segurança centralizada**: Autenticação no Gateway
- **Microsserviços isolados**: Não expostos externamente

#### Por que não usar Service Mesh (Istio/Linkerd)?

**Service Mesh:**
- Infraestrutura complexa (sidecar proxies)
- Melhor para **dezenas/centenas** de microsserviços
- Observabilidade, retry, circuit breaker automáticos

**API Gateway:**
- **Simples**: Apenas um container adicional
- **Suficiente**: Para 2-5 microsserviços
- **Controle explícito**: Lógica de roteamento no código
- **Educacional**: Mais fácil entender o fluxo

#### Por que não implementar Saga Pattern para transações distribuídas?

**Saga Pattern** (compensação em caso de falha):

```python
# Se falhar no passo 4, desfaz passos anteriores
try:
    criar_aluguel()
    decrementar_estoque()
except:
    cancelar_aluguel()  # Compensa a transação
```

**Por que não foi implementado:**
- Adiciona complexidade significativa
- Requer armazenar estado de cada passo
- Foco do desafio é demonstrar comunicação, não gerenciamento de transações
- Em produção real, seria **altamente recomendado**

**Limitação atual:**
No código implementado, se o Records Service falhar ao decrementar o estoque após criar o aluguel, haverá **inconsistência de dados** (aluguel registrado, mas estoque não atualizado). O Saga Pattern resolveria isso com **transações compensatórias**. Esta simplificação foi intencional para focar na arquitetura de microsserviços e comunicação HTTP.

#### Por que usar `depends_on` sem health check?

```yaml
gateway:
  depends_on:
    - records-service
    - rentals-service
```

**Sequência:**
1. Records Service inicia
2. Rentals Service inicia
3. Gateway inicia (após os dois iniciarem)

**Limitação:**
- `depends_on` garante apenas que containers **iniciaram**
- Não garante que Flask está **pronto** para receber requisições
- Gateway pode falhar nas primeiras requisições

**Solução ideal (não implementada por simplicidade):**

```yaml
gateway:
  depends_on:
    records-service:
      condition: service_healthy
    rentals-service:
      condition: service_healthy

records-service:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
```

## 💿 Dados do Sistema

### **Catálogo de Vinis (Records Service)**

| ID | Título | Artista | Gênero | Ano | Preço/Dia | Disponível |
|----|--------|---------|--------|-----|-----------|------------|
| 1 | After Laughter | Paramore | Pop Rock | 2017 | R$ 15 | 2/3 |
| 2 | D>E>A>T>H>M>E>T>A>L | Panchiko | Shoegaze | 2000 | R$ 18 | 1/2 |
| 3 | Petals For Armor | Hayley Williams | Indie | 2020 | R$ 20 | 3/4 |
| 4 | One More Light | Linkin Park | Pop Rock | 2017 | R$ 16 | 2/2 |
| 5 | Meteora (Bonus Edition) | Linkin Park | Rock Alternativo | 2003 | R$ 17 | 1/1 |
| 6 | Electra Heart (Deluxe) | MARINA | Electropop | 2012 | R$ 14 | 2/2 |
| 7 | The Rise and Fall of a Midwest Princess | Chappell Roan | Pop Alternativo | 2023 | R$ 19 | 0/2 |
| 8 | Hamilton (Original Broadway Cast Recording) | Original Broadway Cast of Hamilton | Musical | 2015 | R$ 16 | 1/1 |
| 9 | Ego Death At Bachalorette Party | Hayley Williams | Indie | 2025 | R$ 17 | 2/3 |
| 10 | Violeta | Terno Rei | Rock Alternativo | 2019 | R$ 13 | 3/3 |

### **Clientes Cadastrados (Rentals Service)**

| ID | Nome | Tier | Aluguéis Ativos | Limite | Gênero Favorito |
|----|------|------|-----------------|--------|-----------------|
| 1 | Paulo Rosado | Gold | 0/5 | 5 | Musical |
| 2 | Sophia Gallindo | Silver | 0/3 | 3 | Indie |
| 3 | Gabriel Melo | Bronze | 0/2 | 2 | Rock Alternativo |
| 4 | Vinicius de Andrade | Gold | 0/5 | 5 | Rock Alternativo |
| 5 | Gustavo Mourato | Silver | 0/3 | 3 | Shoegaze |
| 6 | Luan Kato | Bronze | 0/3 | 3 | Rock Alternativo |

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```powershell
   cd desafio5
   ```

2. **Suba os containers:**
   ```powershell
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```powershell
   docker-compose ps
   ```

**Resultado esperado:**
```
NAME                    STATUS      PORTS
desafio5-gateway        Up          0.0.0.0:8080->8080/tcp
desafio5-records        Up          (sem portas expostas)
desafio5-rentals        Up          (sem portas expostas)
```

## 📊 Endpoints do Gateway

| Método | Endpoint | Descrição |
|--------|----------|------------|
| GET | `/` | Informações do Gateway e lista de endpoints |
| GET | `/records` | Listar catálogo completo de discos |
| GET | `/records/<id>` | Detalhes de um disco específico |
| GET | `/records/genre/<genre>` | Filtrar discos por gênero |
| GET | `/records/<id>/availability` | Disponibilidade detalhada de um disco |
| GET | `/customers` | Listar todos os clientes |
| GET | `/customers/<id>/profile` | Perfil completo do cliente com estatísticas |
| GET | `/rentals/active` | Listar aluguéis ativos |
| POST | `/rent` | Alugar um disco |
| PUT | `/return/<rental_id>` | Devolver um disco |
| GET | `/recommendations/<customer_id>` | Recomendações personalizadas |
| GET | `/health` | Health check dos serviços |

### Exemplos de Uso

**1. Listar Catálogo:**
```powershell
curl http://localhost:8080/records
```

**2. Detalhes de um Disco:**
```powershell
curl http://localhost:8080/records/2
```

**3. Filtrar por Gênero:**
```powershell
curl http://localhost:8080/records/genre/Indie
```

**4. Perfil do Cliente:**
```powershell
curl http://localhost:8080/customers/1/profile
```

**5. Alugar Disco:**
```powershell
curl -X POST http://localhost:8080/rent -H "Content-Type: application/json" -d '{"customer_id": 1, "record_id": 3, "rental_days": 7}'
```

**6. Devolver Disco:**
```powershell
curl -X PUT http://localhost:8080/return/1
```

**7. Recomendações:**
```powershell
curl http://localhost:8080/recommendations/1
```

**8. Health Check:**
```powershell
curl http://localhost:8080/health
```


## 🧪 Testando o API Gateway

### **Gateway Home**

```powershell
curl http://localhost:8080/
```

**Resposta:** Lista completa de endpoints disponíveis

---

