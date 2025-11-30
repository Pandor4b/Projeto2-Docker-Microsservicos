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

### 1. Arquitetura de Rede Docker

#### Criação da Rede Bridge Customizada

O Docker Compose cria automaticamente uma rede do tipo **bridge** chamada `desafio1-network`:

```yaml
networks:
  desafio1-network:
    driver: bridge
    name: desafio1-network
```

**Por que usar rede customizada ao invés da rede padrão?**

- **DNS automático**: Containers podem se comunicar pelo nome do serviço (ex: `flask-server`)
- **Isolamento**: Containers fora dessa rede não conseguem acessar os serviços
- **Controle**: Permite configurar subnet, gateway e outras opções de rede
- **Segurança**: Melhor controle sobre quem pode se comunicar com quem

**Como funciona a resolução de nomes:**

```
Cliente executa: requests.get("http://flask-server:8080")
        ↓
Docker DNS resolve "flask-server" → IP interno (ex: 172.18.0.2)
        ↓
Requisição HTTP é enviada para o IP do container do servidor
        ↓
Servidor Flask recebe e processa a requisição
        ↓
Resposta retorna para o cliente
```

### 2. Servidor Flask - Funcionamento Detalhado

#### Inicialização do Servidor

```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

**Parâmetros importantes:**
- `host='0.0.0.0'`: Escuta em **todas** as interfaces de rede do container
  - Se fosse `127.0.0.1`, apenas conexões internas ao container funcionariam
  - Com `0.0.0.0`, o servidor aceita conexões de outros containers na mesma rede
- `port=8080`: Porta onde o servidor aguarda requisições
- `debug=True`: Recarrega automaticamente ao detectar mudanças no código

#### Endpoint Principal (`/`)

```python
@app.route('/')
def home():
    global request_count
    request_count += 1
    
    response_data = {
        'message': 'Servidor Flask em andamento!',
        'timestamp': datetime.now().isoformat(),
        'request_number': request_count,
        'container_name': os.getenv('HOSTNAME', 'unknown'),
        'status': 'running',
        'port': 8080
    }
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Requisição #{request_count} recebida")
    
    return jsonify(response_data), 200
```

**Funcionamento passo a passo:**

1. **Recebe requisição HTTP GET**
2. **Incrementa contador global** de requisições (variável compartilhada)
3. **Coleta informações**:
   - Timestamp atual
   - Número da requisição
   - Nome do container (variável de ambiente `HOSTNAME`)
4. **Loga no console** para rastreamento
5. **Retorna JSON** com status 200 (OK)

**Por que usar variável global `request_count`?**
- Mantém estado entre requisições
- Demonstra persistência durante o ciclo de vida do container
- Resetado apenas quando o container é recriado

#### Health Check Endpoint

```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'flask-server'}), 200
```

**Usado pelo Docker para verificar se o container está saudável:**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s      # Verifica a cada 10 segundos
  timeout: 5s        # Timeout de 5 segundos
  retries: 3         # 3 tentativas antes de marcar como unhealthy
  start_period: 10s  # Aguarda 10s antes de começar
```

### 3. Cliente HTTP - Funcionamento Detalhado

#### Loop de Requisições

```python
SERVER_URL = "http://flask-server:8080"

while True:
    try:
        request_counter += 1
        time.sleep(5)
        
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Exibe resposta formatada
            print(f"✅ Requisição bem-sucedida!")
            print(f"Request Number: {data.get('request_number')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor. Tentando novamente...")
    
    except requests.exceptions.Timeout:
        print("⏱️ Timeout na requisição")
```

**Fluxo de execução:**

1. **Aguarda 5 segundos** entre requisições
2. **Tenta conectar** ao servidor usando o nome DNS `flask-server`
3. **Timeout de 5 segundos**: Requisição falha se demorar mais que isso
4. **Trata erros**:
   - `ConnectionError`: Servidor offline ou ainda inicializando
   - `Timeout`: Servidor não respondeu a tempo
   - `KeyboardInterrupt`: Usuário pressionou Ctrl+C
5. **Exibe resposta formatada** com informações do servidor

**Por que usar `timeout=5`?**
- Evita que o cliente fique travado indefinidamente
- Permite detectar problemas de rede ou sobrecarga do servidor
- Valor deve ser maior que o tempo médio de resposta

### 4. Orquestração com Docker Compose

#### Dependências entre Serviços

```yaml
http-client:
  depends_on:
    flask-server:
      condition: service_started
```

**O que isso significa:**
- Docker Compose inicia o `flask-server` **antes** do `http-client`
- `condition: service_started`: Aguarda apenas o container iniciar (não garante que está pronto)
- Por isso o cliente tem tratamento de erro `ConnectionError` no início

**Sequência de inicialização:**

```
1. docker-compose up
2. Cria rede desafio1-network
3. Inicia container flask-server
4. Aguarda flask-server estar "started"
5. Inicia container http-client
6. Cliente tenta conectar ao servidor
```

#### Mapeamento de Portas

```yaml
flask-server:
  ports:
    - "8080:8080"
```

**Formato: `HOST:CONTAINER`**
- `8080` (esquerda): Porta no **host** (seu computador)
- `8080` (direita): Porta no **container**

**Por que mapear portas?**
- Permite acessar o servidor de **fora** do Docker: `http://localhost:8080`
- Cliente HTTP **não precisa** de mapeamento (apenas comunicação interna)

### 5. Fluxo Completo de Comunicação

#### Diagrama de Sequência

```
[docker-compose up]
        │
        ├─> Cria rede bridge "desafio1-network"
        │   Subnet: 172.18.0.0/16 (exemplo)
        │
        ├─> Inicia flask-server
        │   IP: 172.18.0.2 (exemplo)
        │   DNS: flask-server → 172.18.0.2
        │   Escuta em 0.0.0.0:8080 (todas interfaces)
        │
        └─> Inicia http-client
            IP: 172.18.0.3 (exemplo)
            DNS: Consegue resolver "flask-server"
            
[Loop do Cliente - a cada 5 segundos]
        │
        ├─> DNS lookup: "flask-server" → 172.18.0.2
        │
        ├─> TCP Handshake: Cliente (172.18.0.3) → Servidor (172.18.0.2:8080)
        │
        ├─> HTTP GET / HTTP/1.1
        │   Host: flask-server:8080
        │
        ├─> [SERVIDOR] Recebe requisição
        │   - Incrementa contador
        │   - Gera JSON com dados
        │   - Loga no console
        │
        ├─> HTTP/1.1 200 OK
        │   Content-Type: application/json
        │   Body: {"message": "...", "request_number": 42, ...}
        │
        └─> [CLIENTE] Recebe resposta
            - Parse JSON
            - Exibe formatado
            - Aguarda 5 segundos
            - Repete
```

### 6. Decisões Técnicas

#### Por que Flask ao invés de Nginx?

- **Flask**: Framework web Python completo
  - Permite lógica customizada (contador, logs, JSON dinâmico)
  - Fácil adicionar endpoints e funcionalidades
  - Melhor para demonstrar comunicação entre serviços
  
- **Nginx**: Servidor web estático
  - Excelente para servir arquivos estáticos
  - Não permite lógica dinâmica sem configuração adicional
  - Menos flexível para este desafio

#### Por que usar `depends_on`?

- Garante ordem de inicialização
- Evita que o cliente tente conectar antes do servidor existir
- Documentação clara das dependências

#### Por que health check?

- Monitora saúde do servidor continuamente
- Docker pode reiniciar automaticamente se falhar
- Útil em produção para alta disponibilidade


```


## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```bash
   cd desafio1
   ```

2. **Suba os containers:**
   ```bash
   docker-compose up --build
   ```

3. **Verifique os containers:**
   ```bash
   docker-compose ps
   ```

## 🧪 Testando a Comunicação

### 1. Acesse o servidor diretamente

```bash
curl http://localhost:8080
```

### 2. Endpoint de estatísticas

```bash
curl http://localhost:8080/stats
```

### 3. Health check

```bash
curl http://localhost:8080/health
```

### 4. Visualizar logs dos containers

```bash
# Logs do servidor
docker logs -f desafio1-flask-server

# Logs do cliente
docker logs -f desafio1-http-client

# Logs de ambos ao mesmo tempo
docker-compose logs -f
```