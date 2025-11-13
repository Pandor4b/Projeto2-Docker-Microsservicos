# Desafio 1 — Containers em Rede

## 📋 Descrição do Projeto

Este projeto implementa dois containers Docker que se comunicam através de uma rede customizada:
- **Servidor Flask**: Um servidor web Python que responde requisições HTTP na porta 8080
- **Cliente HTTP**: Um container que realiza requisições periódicas ao servidor

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

- **Docker** e **Docker Compose**: Containerização e orquestração
- **Python 3.11**: Linguagem de programação
- **Flask**: Framework web para o servidor
- **Requests**: Biblioteca HTTP para o cliente
- **Docker Bridge Network**: Rede customizada para comunicação

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


## 💡 Decisões Técnicas

- **Flask**: Escolhido pela facilidade de criar endpoints customizados e logging detalhado
- **Python no Cliente**: Biblioteca `requests` oferece melhor tratamento de erros que curl/wget
- **Rede Bridge**: Permite DNS automático entre containers (flask-server resolve para IP)

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

## 🚀 Como Executar o Projeto

### Pré-requisitos

- Docker Desktop instalado e em execução
- Terminal PowerShell ou Command Prompt

### Passo a Passo

1. **Navegue até a pasta do projeto:**
   ```powershell
   cd desafio1
   ```

2. **Inicie os containers com Docker Compose:**
   ```powershell
   docker-compose up -d --build
   ```
   
   Este comando irá:
   - Criar a rede `desafio1-network`
   - Construir as imagens Docker
   - Iniciar os containers em background (`-d`)

3. **Verifique se os containers estão rodando:**
   ```powershell
   docker-compose ps
   ```
   
   Você deve ver 2 containers ativos: `desafio1-flask-server` e `desafio1-http-client`

4. **Acompanhe os logs em tempo real:**
   ```powershell
   docker-compose logs -f
   ```
   
   Pressione `Ctrl+C` para sair da visualização de logs (os containers continuarão rodando)

### 🧪 Testando a Comunicação

1. **Acesse o servidor pelo navegador:**
   - Abra: http://localhost:8080
   - Você verá uma resposta JSON com informações do servidor

2. **Teste com PowerShell/CMD:**
   ```powershell
   # Endpoint principal
   curl http://localhost:8080
   
   # Estatísticas
   curl http://localhost:8080/stats
   
   # Health check
   curl http://localhost:8080/health
   ```

3. **Visualize os logs de cada container separadamente:**
   ```powershell
   # Logs do servidor
   docker logs desafio1-flask-server
   
   # Logs do cliente
   docker logs desafio1-http-client
   ```



### 🛑 Parando os Containers

```powershell
docker-compose down
```

### 🧹 Limpeza Completa

Para remover containers, imagens e rede:

```powershell
docker-compose down --rmi all --volumes
```

## 🔍 Comandos Úteis para Verificação

### Verificar a rede Docker:
```powershell
# Listar redes
docker network ls

# Inspecionar a rede do projeto
docker network inspect desafio1-network
```

### Ver logs específicos:
```powershell
# Logs do servidor (tempo real)
docker logs desafio1-flask-server -f

# Logs do cliente (tempo real)
docker logs desafio1-http-client -f

# Últimas 50 linhas
docker logs desafio1-flask-server --tail 50
```

### Acessar terminal de um container:
```powershell
# Entrar no servidor
docker exec -it desafio1-flask-server sh

# Entrar no cliente
docker exec -it desafio1-http-client sh
```

### Status dos containers:
```powershell
# Via Docker Compose
docker-compose ps

# Via Docker (mostra todos)
docker ps -a
```

---

## 📋 Resumo dos Comandos Principais

```powershell
# Iniciar o projeto
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps

# Parar containers
docker-compose down

# Limpar tudo
docker-compose down --rmi all --volumes
```
