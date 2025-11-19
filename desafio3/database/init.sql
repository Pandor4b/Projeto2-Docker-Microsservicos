-- Script de inicialização do banco de dados

-- Tabela de Pokémon disponíveis
CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    hp INTEGER NOT NULL,
    ataque INTEGER NOT NULL,
    defesa INTEGER NOT NULL,
    ataque_especial INTEGER NOT NULL,
    defesa_especial INTEGER NOT NULL,
    velocidade INTEGER NOT NULL
);

-- Tabela de histórico de batalhas
CREATE TABLE IF NOT EXISTS batalhas (
    id SERIAL PRIMARY KEY,
    pokemon1_id INTEGER NOT NULL,
    pokemon1_nome VARCHAR(50) NOT NULL,
    pokemon2_id INTEGER NOT NULL,
    pokemon2_nome VARCHAR(50) NOT NULL,
    vencedor_id INTEGER NOT NULL,
    vencedor_nome VARCHAR(50) NOT NULL,
    turnos INTEGER NOT NULL,
    data_batalha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pokemon1_id) REFERENCES pokemon(id),
    FOREIGN KEY (pokemon2_id) REFERENCES pokemon(id),
    FOREIGN KEY (vencedor_id) REFERENCES pokemon(id)
);

-- Inserir as 8 Eeveelutions
INSERT INTO pokemon (id, nome, tipo, hp, ataque, defesa, ataque_especial, defesa_especial, velocidade) VALUES
(134, 'Vaporeon', 'Water', 130, 65, 60, 110, 95, 65),
(135, 'Jolteon', 'Electric', 65, 65, 60, 110, 95, 130),
(136, 'Flareon', 'Fire', 65, 130, 60, 95, 110, 65),
(196, 'Espeon', 'Psychic', 65, 65, 60, 130, 95, 110),
(197, 'Umbreon', 'Dark', 95, 65, 110, 60, 130, 65),
(470, 'Leafeon', 'Grass', 65, 110, 130, 60, 65, 95),
(471, 'Glaceon', 'Ice', 65, 60, 110, 130, 95, 65),
(700, 'Sylveon', 'Fairy', 95, 65, 65, 110, 130, 60);

-- Mensagem de confirmação
SELECT 'Banco de dados Pokémon inicializado' AS status;
