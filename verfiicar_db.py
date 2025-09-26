# verificar_db.py
import sqlite3
import os

DB_PATH = 'rpg_database.db'

def verificar_monstros_por_local(localizacao):
    """
    Executa a mesma busca que o comando .explorar faria, mas de forma simples e direta.
    """
    print(f"\n--- Verificando monstros para o local: '{localizacao}' ---")
    
    if not os.path.exists(DB_PATH):
        print(f"ERRO: O arquivo do banco de dados '{DB_PATH}' não foi encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para facilitar a leitura do resultado
    cursor = conn.cursor()

    try:
        # Exatamente a mesma query do bot
        cursor.execute(
            "SELECT * FROM monsters WHERE localizacao = ?",
            (localizacao.lower(),)
        )
        resultados = cursor.fetchall() # Usamos fetchall para ver todos os monstros da área
        
        print(f"-> A busca encontrou {len(resultados)} monstro(s).")

        if resultados:
            print("Detalhes:")
            for monstro in resultados:
                # dict(monstro) converte o resultado para um dicionário fácil de ler
                print(f"  - {dict(monstro)}")
        
    except sqlite3.OperationalError as e:
        print(f"!!! ERRO DE SQL: {e}")
        print("Isso geralmente significa que a tabela 'monsters' ou a coluna 'localizacao' não existe.")
        print("Solução Provável: Apague o arquivo .db e rode 'popular_mundo.py' novamente.")

    finally:
        conn.close()

# --- Execução do Script ---
if __name__ == "__main__":
    print("Iniciando diagnóstico do banco de dados 'rpg_database.db'...")
    verificar_monstros_por_local("floresta")
    verificar_monstros_por_local("caverna")
    verificar_monstros_por_local("pantano")
    print("\n--- Diagnóstico finalizado ---")