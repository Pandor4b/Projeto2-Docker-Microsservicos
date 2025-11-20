# Desafio 5 — Microsserviços com API Gateway

## 📋 Descrição do Projeto

Sistema de **Locadora de Discos de Vinil** implementando o padrão **API Gateway** para centralizar o acesso a dois microsserviços independentes.

**Objetivo:** Demonstrar arquitetura com API Gateway como ponto único de entrada, orquestrando chamadas e agregando dados de múltiplos microsserviços.

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

- **Docker & Docker Compose**: Containerização e orquestração
- **Flask 3.0.0**: Framework web para todos os serviços
- **Python 3.11**: Linguagem de programação
- **Requests 2.31.0**: Biblioteca HTTP para comunicação entre serviços
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
   ```bash
   cd desafio5
   ```

2. **Suba os containers:**
   ```bash
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```bash
   docker-compose ps
   ```

**Resultado esperado:**
```
NAME                    STATUS      PORTS
desafio5-gateway        Up          0.0.0.0:8080->8080/tcp
desafio5-records        Up          (sem portas expostas)
desafio5-rentals        Up          (sem portas expostas)
```

# 🧪 Testando o API Gateway


### **Gateway Home**

```bash
curl http://localhost:8080/
```

**Resposta:** Lista completa de endpoints disponíveis

---

## 📊 Endpoints do Gateway

### **1. Listar Catálogo de Discos**

```bash
curl http://localhost:8080/records
```

### **2. Detalhes de um Disco**

```bash
curl http://localhost:8080/records/2
```

**Resposta:**
```json
{
  "id": 2,
  "title": "D>E>A>T>H>M>E>T>A>L",
  "artist": "Panchiko",
  "genre": "Shoegaze",
  "year": 2000,
  "daily_rental_price": 18.00,
  "available_copies": 1,
  "total_copies": 2
}
```

### **3. Filtrar por Gênero**

```bash
curl http://localhost:8080/records/genre/Indie
```

### **4. Listar Clientes**

```bash
curl http://localhost:8080/customers
```

### **5. Listar Aluguéis Ativos**

```bash
curl http://localhost:8080/rentals/active
```

---


### **6. Disponibilidade Detalhada de um Disco**

```bash
curl http://localhost:8080/records/7/availability
```

**Resposta:**
```json
{
  "record": {
    "id": 7,
    "title": "The Rise and Fall of a Midwest Princess",
    "artist": "Chappell Roan",
    "genre": "Pop Alternativo",
    "daily_price": 19.00
  },
  "availability": {
    "available_copies": 0,
    "total_copies": 2,
    "is_available": false,
    "currently_rented_by": ["Sophia Gallindo", "Gabriel Melo"],
    "next_available": "2025-11-20"
  }
}
```

**O que o Gateway faz:**
1. Busca informações do disco no Records Service
2. Busca aluguéis ativos no Rentals Service
3. Filtra quem está alugando este disco
4. Calcula próxima disponibilidade
5. Retorna dados agregados

---

### **7. Perfil Completo do Cliente**

```bash
curl http://localhost:8080/customers/1/profile
```

**Resposta:**
```json
{
  "customer": {
    "id": 1,
    "name": "Paulo Rosado",
    "membership_tier": "Gold",
    "active_rentals": 1,
    "favorite_genre": "Musical"
  },
  "active_rentals": [
    {
      "record_title": "Meteora (Bonus Edition)",
      "due_date": "2025-11-11",
      "total_cost": 170.00
    }
  ],
  "statistics": {
    "total_rentals": 47,
    "total_spent": 4830.00,
    "favorite_genre": "Musical"
  }
}
```

---

### **8. Alugar Disco**

```bash
curl -X POST http://localhost:8080/rent \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "record_id": 3,
    "rental_days": 7
  }'
```

**Resposta:**
```json
{
  "message": "Aluguel realizado com sucesso",
  "rental": {
    "id": 6,
    "customer_name": "Paulo Rosado",
    "record_title": "Petals For Armor",
    "rental_days": 7,
    "total_cost": 140.00,
    "due_date": "2025-11-26"
  },
  "orchestrated_by": "gateway"
}
```

---

### **9. Devolver Disco**

```bash
curl -X PUT http://localhost:8080/return/1
```



### **10. Recomendações Personalizadas**

```bash
curl http://localhost:8080/recommendations/1
```

**Resposta:**
```json
{
  "customer": {
    "id": 1,
    "name": "Paulo Rosado",
    "favorite_genre": "Musical"
  },
  "recommendations": [
    {
      "title": "Hamilton (Original Broadway Cast Recording)",
      "artist": "Original Broadway Cast of Hamilton",
      "available_copies": 1
    }
  ],
  "generated_by": "gateway"
}
```


---


## 📊 Health Check dos Serviços

```bash
curl http://localhost:8080/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "gateway": "healthy",
  "services": {
    "records_service": "healthy",
    "rentals_service": "healthy"
  },
  "timestamp": "2025-11-19T10:30:00"
}
```

---

## 🔧 Comandos Úteis

```bash
# Iniciar sistema
docker-compose up --build

# Logs de todos os serviços
docker-compose logs -f

# Logs específicos
docker logs -f desafio5-gateway
docker logs -f desafio5-records
docker logs -f desafio5-rentals

# Parar sistema
docker-compose down

# Reconstruir
docker-compose up --build --force-recreate

# Status dos containers
docker-compose ps
```

---