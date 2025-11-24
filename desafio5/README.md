# Desafio 5 — Microsserviços com API Gateway

## 📋 Descrição do Projeto

Sistema de **Locadora de Discos de Vinil** implementando o padrão **API Gateway** para centralizar o acesso a dois microsserviços independentes.


## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [💿 Dados do Sistema](#-dados-do-sistema) • [🚀 Executar](#-como-executar) • [📊 Endpoints](#-endpoints-do-gateway) • [🧪 Testes](#-testando-o-api-gateway)

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

