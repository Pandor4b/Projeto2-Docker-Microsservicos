# Desafio 2 — Volumes e Persistência de Dados

## 📋 Descrição do Projeto

Este desafio implementa um sistema de gerenciamento de personagens de RPG usando PostgreSQL, demonstrando **persistência de dados** através de Docker Volumes. Os dados permanecem intactos mesmo após remover e recriar os containers.


---

## 📑 Navegação

[🏗️ Arquitetura](#️-arquitetura-da-solução) • [🔧 Tecnologias](#-tecnologias-utilizadas) • [📁 Estrutura](#-estrutura-do-projeto) • [🔍 Como Funciona](#-como-funciona) • [🚀 Como Executar](#-como-executar) • [🧪 Testes](#-testando-a-persistência)

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────┐
│  Volume: desafio2-dados-rpg                 │
│  (/var/lib/postgresql/data)                 │
│              ▲                              │
│              │ Persiste dados               │
│              │                              │
│  ┌───────────┴──────────┐                  │
│  │  PostgreSQL          │                  │
│  │  (desafio2-postgres-db)                 │
│  └───────────┬──────────┘                  │
│              │                              │
│              │ Conexão                      │
│              ▼                              │
│  ┌──────────────────────┐                  │
│  │  App Python          │                  │
│  │  (desafio2-rpg-app)  │                  │
│  └──────────────────────┘                  │
└─────────────────────────────────────────────┘
```

## 🔧 Tecnologias Utilizadas

- **Docker**: Containerização, orquestração e volumes
- **Python 3.11**: Linguagem de programação
- **PostgreSQL 15**: Banco de dados relacional
- **psycopg2**: Driver PostgreSQL para Python

## 📁 Estrutura do Projeto

```
desafio2/
├── database/
│   └── rpg_db.sql         # Script SQL de inicialização
├── app/
│   ├── app.py             # Aplicação Python (CRUD)
│   ├── Dockerfile         # Imagem da aplicação
│   └── requirements.txt   # psycopg2-binary
├── docker-compose.yml     # Orquestração (PostgreSQL + App + Volume)
└── README.md
```

## 🔍 Como Funciona

### 1. Volumes Docker - Persistência de Dados

#### Conceito de Volume

Um **volume Docker** é um diretório que existe **fora** do sistema de arquivos do container:

```yaml
volumes:
  dados_postgres:
    name: desafio2-dados-rpg
```

**Diferença entre Volume e Container:**

| Aspecto | Container | Volume |
|---------|-----------|--------|
| Localização | Sistema de arquivos do container | Host (gerenciado pelo Docker) |
| Persistência | Perdido ao remover container | Permanece após remoção |
| Performance | Normal | Otimizada para I/O |
| Compartilhamento | Isolado | Pode ser compartilhado entre containers |

#### Mapeamento do Volume

```yaml
postgres-db:
  volumes:
    - dados_postgres:/var/lib/postgresql/data
```

**Como funciona:**
- `dados_postgres`: Nome do volume (criado pelo Docker)
- `/var/lib/postgresql/data`: Diretório **dentro** do container onde o PostgreSQL armazena dados
- Dados escritos nesse diretório são **redirecionados** para o volume

### 2. Inicialização do Banco de Dados

#### Script SQL Automático

```yaml
postgres-db:
  volumes:
    - ./database/rpg_db.sql:/docker-entrypoint-initdb.d/rpg_db.sql
```

**Funcionamento do `/docker-entrypoint-initdb.d/`:**

1. PostgreSQL verifica se o volume está **vazio** (primeira inicialização)
2. Se vazio, executa **todos** os scripts `.sql` e `.sh` em ordem alfabética
3. Se volume já tem dados, **ignora** os scripts (não reexecuta)

**Conteúdo do `rpg_db.sql`:**

```sql
CREATE TABLE IF NOT EXISTS personagens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    classe VARCHAR(50) NOT NULL,
    raca VARCHAR(50) NOT NULL,
    nivel INTEGER DEFAULT 1,
    pontos_vida INTEGER NOT NULL,
    forca INTEGER NOT NULL,
    destreza INTEGER NOT NULL,
    inteligencia INTEGER NOT NULL
);

INSERT INTO personagens (nome, classe, raca, nivel, pontos_vida, forca, destreza, inteligencia)
VALUES 
    ('Thorin Escudo de Carvalho', 'Guerreiro', 'Anão', 5, 85, 18, 12, 10),
    ('Elara Vento da Lua', 'Mago', 'Elfo', 4, 32, 8, 14, 18),
    ('Grimm Sombra Furtiva', 'Ladino', 'Halfling', 3, 45, 10, 18, 12);
```

**Sequência de inicialização:**

```
1. Docker cria container PostgreSQL
2. Monta volume "dados_postgres" em /var/lib/postgresql/data
3. Verifica se volume está vazio
4. Se vazio:
   - Inicializa cluster PostgreSQL
   - Executa rpg_db.sql
   - Cria tabela "personagens"
   - Insere 3 personagens iniciais
5. Se já tem dados:
   - Usa dados existentes
   - Pula inicialização
```

### 3. Aplicação Python - Conexão e Operações

#### Conexão com PostgreSQL

```python
DB_CONFIG = {
    'host': 'postgres-db',        # Nome do serviço no docker-compose
    'database': 'rpg_db',          # Nome do banco
    'user': 'mestre',              # Usuário criado
    'password': 'dado20'           # Senha definida
}

def conectar_banco():
    tentativas = 0
    while tentativas < 5:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            print("[OK] Conectado ao banco de dados RPG!")
            return conn
        except psycopg2.OperationalError:
            tentativas += 1
            print(f"[AGUARDANDO] Banco inicializando... (tentativa {tentativas}/5)")
            time.sleep(2)
```

**Por que usar retry loop?**
- PostgreSQL pode demorar alguns segundos para inicializar
- `depends_on` garante que o container está **rodando**, mas não que está **pronto**
- Retry com sleep evita falha na primeira tentativa

**Resolução de DNS Docker:**

```
"postgres-db" → Docker DNS interno → IP do container (ex: 172.19.0.2:5432)
```

#### Operações CRUD

**1. Listar Personagens:**

```python
def listar_personagens(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personagens ORDER BY nivel DESC, id")
    personagens = cursor.fetchall()
    
    for char in personagens:
        print(f"[{char[0]}] {char[1]}")  # ID e Nome
        print(f"    Classe: {char[2]} | Raça: {char[3]} | Nível: {char[4]}")
        print(f"    Vida: {char[5]} | FOR: {char[6]} | DES: {char[7]} | INT: {char[8]}")
```

**2. Criar Personagem:**

```python
def criar_personagem(conn, nome, classe, raca, nivel, vida, forca, destreza, inteligencia):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO personagens 
           (nome, classe, raca, nivel, pontos_vida, forca, destreza, inteligencia) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (nome, classe, raca, nivel, vida, forca, destreza, inteligencia)
    )
    conn.commit()  # IMPORTANTE: Confirma a transação
```

**Por que `conn.commit()`?**
- PostgreSQL usa **transações**
- Sem `commit()`, mudanças não são salvas permanentemente
- Se o programa crashar antes do commit, INSERT é revertido

**3. Contar Personagens:**

```python
def contar_personagens(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personagens")
    total = cursor.fetchone()[0]
    return total
```

### 4. Ciclo de Vida dos Dados

#### Primeira Execução

```
[docker-compose up]
        ↓
Volume "desafio2-dados-rpg" NÃO existe
        ↓
Docker cria volume vazio
        ↓
PostgreSQL detecta volume vazio
        ↓
Executa /docker-entrypoint-initdb.d/rpg_db.sql
        ↓
Cria tabela "personagens"
        ↓
Insere 3 personagens iniciais
        ↓
[App Python inicia]
        ↓
Lista 3 personagens existentes
        ↓
Cria novo personagem: "Kael Brasas Ardentes"
        ↓
Dados gravados no VOLUME (não no container!)
        ↓
Total: 4 personagens
```

#### Remoção e Recriação (Persistência)

```
[docker-compose down]
        ↓
Container PostgreSQL: REMOVIDO
Container App Python: REMOVIDO
Rede Docker: REMOVIDA
Volume desafio2-dados-rpg: MANTIDO
        ↓
[docker-compose up]
        ↓
Novos containers criados
        ↓
Volume EXISTENTE é remontado
        ↓
PostgreSQL detecta dados no volume
        ↓
NÃO executa script de inicialização
        ↓
Usa dados existentes
        ↓
[App Python inicia]
        ↓
Lista personagens: 4 personagens (incluindo Kael!)
        ↓
DADOS PERSISTIRAM!
```

#### Destruição Completa

```
[docker-compose down -v]
        ↓
Container PostgreSQL: REMOVIDO
Container App Python: REMOVIDO
Rede Docker: REMOVIDA
Volume desafio2-dados-rpg: REMOVIDO (-v flag)
        ↓
[docker-compose up]
        ↓
Volta ao estado inicial (3 personagens)
```

### 5. Rede Docker e Comunicação

#### Configuração de Rede

```yaml
networks:
  desafio2-network:
    driver: bridge
    name: desafio2-network
```

**Containers na mesma rede:**

```
┌────────────────────────────────────────────┐
│  Rede: desafio2-network (172.19.0.0/16)   │
│                                            │
│  postgres-db (172.19.0.2:5432)            │
│       ↑                                    │
│       │ Conexão TCP                        │
│       │ psycopg2.connect()                 │
│       │                                    │
│  app (172.19.0.3)                         │
│                                            │
└────────────────────────────────────────────┘
```

**Portas:**
- PostgreSQL escuta em `5432` (porta padrão)
- Mapeamento `5432:5432` permite acesso do host também
- App não precisa mapear portas (apenas comunicação interna)

### 6. Variáveis de Ambiente

#### Configuração do PostgreSQL

```yaml
postgres-db:
  environment:
    POSTGRES_DB: rpg_db          # Nome do banco a criar
    POSTGRES_USER: mestre         # Superusuário
    POSTGRES_PASSWORD: dado20     # Senha do superusuário
```

**Processo de criação:**

1. Container inicia
2. PostgreSQL lê variáveis de ambiente
3. Cria banco "rpg_db"
4. Cria usuário "mestre" com senha "dado20"
5. Concede privilégios totais ao usuário

#### String de Conexão Resultante

```python
# No app.py
conn = psycopg2.connect(
    host="postgres-db",      # Resolvido via DNS Docker
    database="rpg_db",       # Banco criado pela variável POSTGRES_DB
    user="mestre",           # Usuário criado pela variável POSTGRES_USER
    password="dado20"        # Senha definida pela variável POSTGRES_PASSWORD
)
```

### 7. Dockerfile da Aplicação

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```

**Funcionamento:**
1. Base: Imagem Python 3.11 (versão slim para menor tamanho)
2. Define `/app` como diretório de trabalho
3. Copia `requirements.txt` e instala dependências (`psycopg2-binary`)
4. Copia código da aplicação
5. Comando padrão: executa `python app.py`

**Por que `psycopg2-binary`?**
- `psycopg2`: Requer compilação e dependências do PostgreSQL
- `psycopg2-binary`: Versão pré-compilada, mais fácil de instalar
- Ideal para desenvolvimento e testes

### 8. Decisões Técnicas

#### Por que PostgreSQL ao invés de SQLite?

- **PostgreSQL**: Banco cliente-servidor
  - Permite conexões de múltiplos containers
  - Simula ambiente de produção real
  - Melhor demonstração de comunicação entre containers
  
- **SQLite**: Banco baseado em arquivo
  - Apenas um processo pode escrever por vez
  - Menos realista para microsserviços
  - Sem autenticação/usuários

#### Por que usar volume nomeado ao invés de bind mount?

```yaml
# Volume nomeado (usado)
volumes:
  - dados_postgres:/var/lib/postgresql/data

# Bind mount (alternativa)
volumes:
  - ./data:/var/lib/postgresql/data
```

**Vantagens do volume nomeado:**
- ✅ Gerenciado pelo Docker (backup facilitado)
- ✅ Melhor performance (especialmente Windows/Mac)
- ✅ Funciona em qualquer plataforma
- ✅ Isolado do código fonte

**Quando usar bind mount:**
- Desenvolvimento local (hot reload de código)
- Arquivos de configuração customizados

#### Por que `depends_on` sem health check?

```yaml
app:
  depends_on:
    - postgres-db
```

**Opção atual:**
- App aguarda container PostgreSQL **iniciar**
- Implementa retry loop em Python
- Mais simples e eficaz para este caso

**Alternativa com health check:**
```yaml
app:
  depends_on:
    postgres-db:
      condition: service_healthy
postgres-db:
  healthcheck:
    test: ["CMD", "pg_isready", "-U", "mestre"]
```
- Requer comando adicional no container

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```bash
   cd desafio2
   ```

2. **Suba os containers:**
   ```bash
   docker-compose up -d --build
   ```

3. **Veja os logs:**
   ```bash
   docker logs desafio2-rpg-app
   ```

## 🧪 Testando a Persistência

### Cenário 1: Primeira Execução

```bash
docker-compose up -d --build
docker logs desafio2-rpg-app
```

**Output esperado:**
```
================================================================================
SISTEMA DE GERENCIAMENTO DE PERSONAGENS - RPG DE MESA
================================================================================
Data/Hora: 2025-11-12 14:30:00

[OK] Conectado ao banco de dados RPG!

Personagens cadastrados:

================================================================================
FICHA DE PERSONAGENS - RPG DE MESA
================================================================================

[1] Thorin Escudo de Carvalho
    Classe: Guerreiro | Raça: Anão | Nível: 5
    Vida: 85 | FOR: 18 | DES: 12 | INT: 10

[2] Elara Vento da Lua
    Classe: Mago | Raça: Elfo | Nível: 4
    Vida: 32 | FOR: 8 | DES: 14 | INT: 18

[3] Grimm Sombra Furtiva
    Classe: Ladino | Raça: Halfling | Nível: 3
    Vida: 45 | FOR: 10 | DES: 18 | INT: 12

================================================================================

Criando novo personagem...

[SUCESSO] Personagem 'Kael Brasas Ardentes' criado com sucesso!

Total de personagens na campanha: 4

[INFO] Conexão com banco encerrada.
```

### Cenário 2: Teste de Persistência

```bash
# Remove containers
docker-compose down

# Verifica que o volume ainda existe
docker volume ls
# Saída: desafio2-dados-rpg

# Recria containers
docker-compose up -d

# Executa app novamente
docker-compose run --rm app python app.py
```

**Resultado:** Os 4 personagens criados anteriormente continuam no banco! ✅

### Cenário 3: Destruir Dados

```bash
# Remove containers E volume
docker-compose down -v

# Volume removido
docker volume ls
# Saída: (sem desafio2-dados-rpg)
```

