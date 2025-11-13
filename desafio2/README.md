# Desafio 2 — Volumes e Persistência de Dados

## 📋 Descrição do Projeto

Este desafio implementa um sistema de gerenciamento de personagens de RPG usando PostgreSQL, demonstrando **persistência de dados** através de Docker Volumes. Os dados permanecem intactos mesmo após remover e recriar os containers.

**Objetivo:** Demonstrar que volumes Docker armazenam dados fora do ciclo de vida dos containers.

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

- **Docker** e **Docker Compose**
- **PostgreSQL 15-alpine**
- **Python 3.11** com psycopg2
- **Docker Named Volume**

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

## 🚀 Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando

### Comandos

1. **Navegue até a pasta:**
   ```powershell
   cd desafio2
   ```

2. **Suba os containers:**
   ```powershell
   docker-compose up -d --build
   ```

3. **Veja os logs:**
   ```powershell
   docker logs desafio2-rpg-app
   ```

## 🧪 Demonstração de Persistência

### Cenário 1: Primeira Execução

```powershell
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

```powershell
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

```powershell
# Remove containers E volume
docker-compose down -v

# Volume removido
docker volume ls
# Saída: (sem desafio2-dados-rpg)
```

## 📊 Comandos Úteis

```powershell
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar (mantém volume)
docker-compose down

# Parar e remover volume
docker-compose down -v

# Executar app manualmente
docker-compose run --rm app python app.py

# Acessar PostgreSQL
docker exec -it desafio2-postgres-db psql -U mestre -d rpg_db

# Inspecionar volume
docker volume inspect desafio2-dados-rpg
```
