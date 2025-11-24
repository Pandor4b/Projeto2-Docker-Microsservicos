# Desafio 1 — Containers em Rede

## 📋 Descrição do Projeto

Este projeto implementa dois containers Docker que se comunicam através de uma rede customizada:
- **Servidor Flask**: Um servidor web Python que responde requisições HTTP na porta 8080
- **Cliente HTTP**: Um container que realiza requisições periódicas ao servidor

---

## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🔍 Como Funciona](#-como-funciona) • [🚀 Executar](#-como-executar) • [🧪 Testes](#-testando-a-comunicação)

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────┐
│                  Rede Docker Customizada                │
│                  (desafio1-network)                     │
│                                                         │
│  ┌──────────────────┐        ┌──────────────────┐     │
│  │  Flask Server    │◄───────┤   HTTP Client    │     │
│  │  (Port 8080)     │        │  (Requisições)   │     │
│  │                  │────────►│  a cada 5s      │     │
│  └──────────────────┘        └──────────────────┘     │
│         ▲                                              │
│         │                                              │
└─────────┼──────────────────────────────────────────────┘
          │
          │ Port Mapping
          │ 8080:8080
          ▼
    ┌──────────┐
    │   Host   │
    └──────────┘
```

## 🔧 Tecnologias Utilizadas

- **Docker**: Containerização, orquestração e redes
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web para o servidor
- **Requests**: Biblioteca HTTP para comunicação

## 📁 Estrutura do Projeto

```
desafio1/
├── server/                # Servidor Flask
│   ├── app.py             # Código do servidor web
│   ├── Dockerfile         # Imagem Docker do servidor
│   └── requirements.txt   # Dependências Python (Flask)
│
├── client/                # Cliente HTTP
│   ├── client.py          # Código do cliente
│   ├── Dockerfile         # Imagem Docker do cliente
│   └── requirements.txt   # Dependências Python (requests)
│
├── docker-compose.yml     # Orquestração dos containers
└── README.md              # Este arquivo
```



## 🔍 Como Funciona

### Servidor Flask (`server/app.py`)

O servidor implementa três endpoints:

1. **`/` (raiz)**: Endpoint principal que:
   - Incrementa um contador de requisições
   - Retorna JSON com informações da requisição
   - Loga cada acesso no console

2. **`/health`**: Health check para monitoramento

3. **`/stats`**: Estatísticas do servidor

**Características importantes:**
- `host='0.0.0.0'`: Permite conexões externas ao container
- `port=8080`: Porta configurada conforme requisito
- Logs detalhados com timestamp

### Cliente HTTP (`client/client.py`)

O cliente executa um loop infinito que:

1. Faz requisição HTTP GET para `http://desafio1-flask-server:8080`
2. Exibe resposta formatada com informações
3. Aguarda 5 segundos
4. Repete o processo

**Tratamento de erros:**
- `ConnectionError`: Servidor ainda não iniciado
- `Timeout`: Requisição demorou demais
- `KeyboardInterrupt`: Interrupção manual

### Rede Docker

A rede `desafio1-network` é do tipo **bridge** e permite:

- ✅ Comunicação entre containers pelo **nome do serviço** (DNS automático)
- ✅ Isolamento de outras redes Docker
- ✅ Mapeamento de portas para o host

No `docker-compose.yml`:
```yaml
networks:
  desafio1-network:
    driver: bridge
    name: desafio1-network
```

Ambos os containers estão conectados a essa rede:
```yaml
services:
  desafio1-flask-server:
    networks:
      - desafio1-network
  
  desafio1-http-client:
    networks:
      - desafio1-network
```

### Fluxo de Comunicação

1. **Inicialização**:
   - Docker cria a rede `desafio1-network`
   - Servidor Flask inicia na porta 8080
   - Cliente aguarda 3 segundos para garantir que o servidor está pronto

2. **Comunicação**:
   - Cliente faz `GET http://desafio1-flask-server:8080/`
   - Docker resolve `desafio1-flask-server` para o IP do container
   - Servidor recebe, processa e responde
   - Cliente exibe resposta formatada
   - Aguarda 5 segundos e repete

3. **Logs**:
   - Servidor: registra cada requisição recebida
   - Cliente: exibe detalhes da resposta

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```powershell
   cd desafio1
   ```

2. **Suba os containers:**
   ```powershell
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```powershell
   docker-compose ps
   ```

## 🧪 Testando a Comunicação

### 1. Acesse o servidor diretamente

```powershell
curl http://localhost:8080
```

### 2. Endpoint de estatísticas

```powershell
curl http://localhost:8080/stats
```

### 3. Health check

```powershell
curl http://localhost:8080/health
```

### 4. Visualizar logs dos containers

```powershell
# Logs do servidor
docker logs -f desafio1-flask-server

# Logs do cliente
docker logs -f desafio1-http-client
```