import requests
import time
from datetime import datetime
import sys

# URL do servidor (nome do serviço no docker-compose)
SERVER_URL = "http://flask-server:8080"

def make_request(endpoint="/"):
    try:
        response = requests.get(f"{SERVER_URL}{endpoint}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n{'='*60}")
            print(f"[{timestamp}] ✅ Requisição bem-sucedida!")
            print(f"{'='*60}")
            print(f"Status Code: {response.status_code}")
            print(f"Mensagem: {data.get('message', 'N/A')}")
            print(f"Request Number: {data.get('request_number', 'N/A')}")
            print(f"Server Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"Container: {data.get('container_name', 'N/A')}")
            print(f"{'='*60}\n")
            
            return True
        else:
            print(f"Erro: Status Code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}]  Não foi possível conectar ao servidor. Tentando novamente...")
        return False
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%H:%M:%S')}]  Timeout na requisição")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}]  Erro inesperado: {str(e)}")
        return False

def main():
    print("Cliente iniciado!")
    print(f"Servidor alvo: {SERVER_URL}")
    print("Fazendo requisições a cada 5 segundos...\n")
    
    request_counter = 0
    
    # Loop infinito fazendo requisições periódicas
    while True:
        try:
            request_counter += 1
            print(f"📡 Enviando requisição #{request_counter}...")
            
            make_request("/")
            
            # Aguarda 5 segundos antes da próxima requisição
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\nCliente interrompido pelo usuário")
            print(f"Total de requisições enviadas: {request_counter}")
            sys.exit(0)

if __name__ == "__main__":
    # Aguarda um pouco para garantir que o servidor esteja pronto
    print("Aguardando servidor inicializar...")
    time.sleep(3)
    main()
