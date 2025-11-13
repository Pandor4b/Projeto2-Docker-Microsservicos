import psycopg2
import time
import sys
from datetime import datetime

DB_CONFIG = {
    'host': 'postgres-db',
    'database': 'rpg_db',
    'user': 'mestre',
    'password': 'dado20'
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
    
    print("[ERRO] Não foi possível conectar ao banco!")
    sys.exit(1)

def listar_personagens(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personagens ORDER BY nivel DESC, id")
    personagens = cursor.fetchall()
    
    print("\n" + "="*80)
    print("FICHA DE PERSONAGENS - RPG DE MESA")
    print("="*80)
    
    if personagens:
        for char in personagens:
            print(f"\n[{char[0]}] {char[1]}")
            print(f"    Classe: {char[2]} | Raça: {char[3]} | Nível: {char[4]}")
            print(f"    Vida: {char[5]} | FOR: {char[6]} | DES: {char[7]} | INT: {char[8]}")
    else:
        print("Nenhum personagem criado ainda.")
    
    print("\n" + "="*80 + "\n")
    cursor.close()

def criar_personagem(conn, nome, classe, raca, nivel, vida, forca, destreza, inteligencia):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO personagens 
           (nome, classe, raca, nivel, pontos_vida, forca, destreza, inteligencia) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (nome, classe, raca, nivel, vida, forca, destreza, inteligencia)
    )
    conn.commit()
    print(f"[SUCESSO] Personagem '{nome}' criado com sucesso!")
    cursor.close()

def contar_personagens(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personagens")
    total = cursor.fetchone()[0]
    cursor.close()
    return total

def main():
    print("\n" + "="*80)
    print("SISTEMA DE GERENCIAMENTO DE PERSONAGENS - RPG DE MESA")
    print("="*80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Conecta ao banco
    conn = conectar_banco()
    
    # Lista personagens existentes
    print("\nPersonagens cadastrados:")
    listar_personagens(conn)
    
    # Cria um novo personagem
    print("Criando novo personagem...\n")
    criar_personagem(
        conn,
        nome="Kael Brasas Ardentes",
        classe="Paladino",
        raca="Humano",
        nivel=6,
        vida=95,
        forca=16,
        destreza=10,
        inteligencia=14
    )
    
    # Lista novamente
    print("\nLista atualizada de personagens:")
    listar_personagens(conn)
    
    # Mostra total
    total = contar_personagens(conn)
    print(f"Total de personagens na campanha: {total}\n")
    
    # Fecha conexão
    conn.close()
    print("[INFO] Conexão com banco encerrada.")
    print("\nOs personagens foram salvos no volume Docker!")
    print("Mesmo se remover o container, os dados persistem.\n")

if __name__ == "__main__":
    main()
