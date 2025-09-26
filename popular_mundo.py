# popular_mundo.py
import sqlite3
import os
import json
import sys
sys.path.append('.')

try:
    from rpg.database import setup_database, DB_PATH
    from rpg.game_data import ITENS_GERAIS, ARMAS, ARMADURAS, ESCUDOS, ACESSORIOS, MONSTROS, DROP_TABLES
except ImportError as e:
    print(f"Erro fatal ao importar módulos: {e}")
    exit()

def popular_itens(cursor):
    print("Processando itens...")
    TODOS_OS_ITENS = {**ITENS_GERAIS, **ARMAS, **ARMADURAS, **ESCUDOS, **ACESSORIOS}
    itens_para_db = []
    
    for item_data in TODOS_OS_ITENS.values():
        nome = item_data.get("nome")
        tipo = item_data.get("tipo", "Item")
        peso = item_data.get("peso", 0.0)
        raridade = item_data.get("raridade", "common")
        slot = item_data.get("slot", "none")
        
        bonus_stats_json = json.dumps(item_data.get("stats")) if item_data.get("stats") else None
        efeitos_json = json.dumps(item_data.get("efeitos")) if item_data.get("efeitos") else None
        
        itens_para_db.append((nome, tipo, peso, raridade, slot, bonus_stats_json, efeitos_json))
    
    cursor.executemany("INSERT OR IGNORE INTO items (nome, tipo, peso, raridade, slot, bonus_stats, efeitos) VALUES (?, ?, ?, ?, ?, ?, ?)", itens_para_db)
    print(f"-> {cursor.rowcount} itens foram adicionados.")

# (As outras funções de popular monstros e drops seguirão esta nova simplicidade)

if __name__ == "__main__":
    print("Iniciando script para popular o banco de dados...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("-> Banco de dados antigo removido.")

    setup_database() # Esta função precisa estar atualizada no seu database.py!
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    popular_itens(cursor)
    # popular_monstros(cursor)
    # definir_drops(cursor)
    
    conn.commit()
    conn.close()
    print("\n✅ Mundo populado com a nova estrutura!")