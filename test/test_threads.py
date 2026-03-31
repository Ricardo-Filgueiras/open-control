import threading
import os
import sys
import time

# Adiciona o diretório 'src' ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.database.database import Database

def worker(thread_id):
    try:
        db = Database()
        print(f"Thread {thread_id} iniciando...")
        # Simular uma operação de escrita (usando OR REPLACE para permitir re-execução)
        db.execute(
            "INSERT OR REPLACE INTO app_metadata (key, value) VALUES (?, ?)",
            (f"thread_test_{thread_id}", f"value_{thread_id}")
        )
        print(f"✅ Thread {thread_id} escreveu com sucesso!")
        
        # Simular uma leitura
        val = db.fetch_one(
            "SELECT value FROM app_metadata WHERE key = ?",
            (f"thread_test_{thread_id}",)
        )
        print(f"✅ Thread {thread_id} leu: {val[0]}")
    except Exception as e:
        print(f"❌ Erro na Thread {thread_id}: {e}")

if __name__ == "__main__":
    print("Iniciando teste de multi-threading para o Banco de Dados...")
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    print("\nTeste concluído. Se nenhuma Thread falhou com 'ProgrammingError', a correção está funcionando!")
