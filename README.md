# Projeto 2 - Docker & Microsserviços

> **Disciplina:** Fundamentos de Computação Concorrente, Paralela e Distribuída  
> **Curso:** Ciência da Computação - Cesar School  
> **Período:** 5º Período  

## 📋 Sobre o Projeto

Este repositório contém **5 desafios** sobre Docker e Microsserviços, cada um explorando diferentes conceitos de containerização, orquestração e arquitetura distribuída.

---

## 🎯 Desafios

### [Desafio 1 — Containers em Rede](./desafio1/)
**Conceito:** Comunicação entre containers em rede customizada  
**Tecnologias:** Docker Networks, Flask, Python

Dois containers se comunicam através de uma rede Docker customizada. Um servidor Flask responde requisições de um cliente que faz chamadas periódicas a cada 5 segundos.


[Ver documentação completa →](./desafio1/README.md)

---

### [Desafio 2 — Volumes e Persistência](./desafio2/)
**Conceito:** Persistência de dados com Docker Volumes  
**Tecnologias:** PostgreSQL, Docker Volumes, Python

Implementa um banco de dados PostgreSQL com persistência de dados usando volumes. Os dados sobrevivem mesmo após remover e recriar containers, permitindo operações CRUD em personagens de RPG.


[Ver documentação completa →](./desafio2/README.md)

---

### [Desafio 3 — Docker Compose e Orquestração](./desafio3/)
**Conceito:** Orquestração de múltiplos serviços interdependentes   
**Tecnologias:** Docker Compose, Flask, PostgreSQL, Redis

Sistema com 3 serviços integrados: API de batalha Flask, banco PostgreSQL para dados dos Pokémon e Redis para cache de batalhas. Demonstra orquestração completa com dependências entre serviços.


[Ver documentação completa →](./desafio3/README.md)

---

### [Desafio 4 — Microsserviços Independentes](./desafio4/)
**Conceito:** Arquitetura de microsserviços com comunicação HTTP  
**Tecnologias:** Flask, HTTP APIs, JSON

Dois microsserviços independentes que se comunicam via HTTP. O Characters Service gerencia personagens e o Survival Stats Service consome esses dados para calcular estatísticas de sobrevivência.

[Ver documentação completa →](./desafio4/README.md)

---

### [Desafio 5 — API Gateway Pattern](./desafio5/)
**Conceito:** Padrão API Gateway como ponto único de entrada  
**Tecnologias:** Flask, API Gateway, Microsserviços, Docker Compose

Implementa o padrão API Gateway com 3 serviços: Gateway (ponto único de entrada), Records Service (catálogo de vinis) e Rentals Service (gestão de aluguéis). Gateway orquestra chamadas e agrega dados de múltiplos serviços.

[Ver documentação completa →](./desafio5/README.md)

---

## 🛠️ Tecnologias Utilizadas

- **Docker**: Containerização, orquestração, redes e volumes
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web para APIs REST
- **PostgreSQL 15**: Banco de dados relacional
- **Redis 7**: Cache em memória
- **Requests**: Biblioteca HTTP para comunicação entre serviços

---

## 📚 Progressão dos Conceitos

Os desafios foram estruturados em ordem crescente de complexidade:

1. **Desafio 1:** Fundamentos de redes Docker
2. **Desafio 2:** Persistência com volumes
3. **Desafio 3:** Orquestração com Docker Compose
4. **Desafio 4:** Arquitetura de microsserviços
5. **Desafio 5:** Padrões avançados (API Gateway)

---

## 🚀 Como Executar

Cada desafio possui instruções detalhadas em seu próprio README. Em geral:

```bash
# Navegue até a pasta do desafio
cd desafio1  

# Execute com Docker Compose
docker-compose up --build

# Para parar os containers
docker-compose down
```

---

## 📖 Estrutura do Repositório

```
Projeto2-FCCPD-Docker-Microsservicos/
├── desafio1/          # Containers em Rede
├── desafio2/          # Volumes e Persistência
├── desafio3/          # Docker Compose (Pokémon Battle)
├── desafio4/          # Microsserviços (Don't Starve Together)
├── desafio5/          # API Gateway (Vinyl Records Shop)
└── README.md          # Este arquivo
```

