-- Script de inicialização do banco de dados
-- Sistema de gerenciamento de personagens de RPG de mesa

CREATE TABLE IF NOT EXISTS personagens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    classe VARCHAR(50) NOT NULL,
    raca VARCHAR(50) NOT NULL,
    nivel INTEGER DEFAULT 1,
    pontos_vida INTEGER NOT NULL,
    forca INTEGER DEFAULT 10,
    destreza INTEGER DEFAULT 10,
    inteligencia INTEGER DEFAULT 10,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insere alguns personagens iniciais
INSERT INTO
    personagens (
        nome,
        classe,
        raca,
        nivel,
        pontos_vida,
        forca,
        destreza,
        inteligencia
    )
VALUES (
        'Thorin Escudo de Carvalho',
        'Guerreiro',
        'Anão',
        5,
        85,
        18,
        12,
        10
    ),
    (
        'Elara Vento da Lua',
        'Mago',
        'Elfo',
        4,
        32,
        8,
        14,
        18
    ),
    (
        'Grimm Sombra Furtiva',
        'Ladino',
        'Halfling',
        3,
        45,
        10,
        18,
        12
    );

-- Mensagem de confirmação
SELECT 'Banco de dados de RPG inicializado com sucesso!' AS status;