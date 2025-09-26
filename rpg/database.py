# rpg/database.py
import sqlite3
import os
import datetime
import json

DB_PATH = 'rpg_database.db'

def setup_database():
    """Cria e atualiza TODAS as tabelas do banco de dados do RPG."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela principal dos jogadores (COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            titulo TEXT,
            raca TEXT NOT NULL,
            classe TEXT NOT NULL,
            nivel INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            exp_para_upar INTEGER DEFAULT 100,
            gold INTEGER DEFAULT 25,
            energia INTEGER DEFAULT 100,
            energia_max INTEGER DEFAULT 100,
            hp INTEGER NOT NULL,
            mp INTEGER NOT NULL,
            hp_max INTEGER NOT NULL,
            mp_max INTEGER NOT NULL,
            forca INTEGER NOT NULL,
            destreza INTEGER NOT NULL,
            inteligencia INTEGER NOT NULL,
            constituicao INTEGER NOT NULL,
            sorte INTEGER NOT NULL,
            last_daily TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_skills (
            user_id TEXT NOT NULL,
            skill_key TEXT NOT NULL,
            PRIMARY KEY (user_id, skill_key),
            FOREIGN KEY (user_id) REFERENCES players (user_id)
        )
    ''')

    # Tabela de itens (COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            peso REAL DEFAULT 0.0,      -- <<-- NOVA COLUNA
            raridade TEXT NOT NULL,
            slot TEXT,
            bonus_stats TEXT,
            efeitos TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            monster_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            hp_max INTEGER NOT NULL,
            ataque INTEGER NOT NULL,
            defesa INTEGER NOT NULL,
            exp_recompensa INTEGER NOT NULL,
            gold_recompensa INTEGER NOT NULL,
            localizacao TEXT
        )
    ''')

    # Tabela de drops (COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monster_drops (
            drop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_id INTEGER,
            item_id INTEGER,
            chance REAL NOT NULL,
            FOREIGN KEY (monster_id) REFERENCES monsters (monster_id),
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    ''')
    
    # Tabela de equipamento (COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            user_id TEXT PRIMARY KEY,
            cabeca INTEGER,
            peitoral INTEGER,
            calcas INTEGER,
            botas INTEGER,
            arma INTEGER,
            acessorio INTEGER,
            luvas INTEGER,
            FOREIGN KEY (user_id) REFERENCES players (user_id),
            FOREIGN KEY (cabeca) REFERENCES items (item_id),
            FOREIGN KEY (peitoral) REFERENCES items (item_id),
            FOREIGN KEY (calcas) REFERENCES items (item_id),
            FOREIGN KEY (botas) REFERENCES items (item_id),
            FOREIGN KEY (arma) REFERENCES items (item_id),
            FOREIGN KEY (acessorio) REFERENCES items (item_id)
        )
    ''')

    # Tabela de inventário (COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES players (user_id),
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    ''')

    # Tabela de efeitos(COMPLETA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_effects (
            effect_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            stat TEXT, -- ex: 'for', 'des', 'defesa'
            amount INTEGER,
            expires_at TEXT, -- Data e hora em que o efeito termina
            FOREIGN KEY (user_id) REFERENCES players (user_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados do RPG (re)configurado com a estrutura completa.")

# --- FUNÇÕES ---
# (Todas as outras funções como get_player, create_player, get_player_inventory, etc. continuam aqui)
# Cole-as a partir daqui se você as removeu, ou apenas confirme que elas já existem abaixo desta linha.

def get_player(user_id):
    """Busca um jogador e seu equipamento no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM players 
        LEFT JOIN equipment ON players.user_id = equipment.user_id 
        WHERE players.user_id = ?
    ''', (str(user_id),))
    player_data = cursor.fetchone()
    conn.close()
    return player_data

def create_player(user_id, nome, raca, classe, stats):
    """Cria um novo jogador e sua entrada de equipamento."""
    if get_player(user_id):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO players (user_id, nome, raca, classe, hp, mp, hp_max, mp_max, forca, destreza, inteligencia, constituicao, sorte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(user_id), nome, raca, classe, stats['hp'], stats['mp'], stats['hp'], stats['mp'], stats['for'], stats['des'], stats['int'], stats['con'], stats['sor']))
    cursor.execute("INSERT INTO equipment (user_id) VALUES (?)", (str(user_id),))
    conn.commit()
    conn.close()

def update_player_energy(user_id, amount):
    """Adiciona ou remove energia de um jogador, respeitando o máximo."""
    player = get_player(user_id)
    if not player:
        return
    nova_energia = min(player['energia'] + amount, player['energia_max'])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET energia = ? WHERE user_id = ?", (nova_energia, str(user_id)))
    conn.commit()
    conn.close()
    return nova_energia

def update_last_daily(user_id):
    """Atualiza o registro do .diario para o momento atual."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET last_daily = ? WHERE user_id = ?", (now_utc, str(user_id)))
    conn.commit()
    conn.close()

def get_all_players_for_regen():
    """Busca todos os jogadores que não estão com a energia no máximo."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM players WHERE energia < energia_max")
    players = cursor.fetchall()
    conn.close()
    return players

def get_player_inventory(user_id):
    """Busca todos os itens no inventário de um jogador."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, inv.quantity 
        FROM inventory inv
        JOIN items i ON inv.item_id = i.item_id
        WHERE inv.user_id = ?
    ''', (str(user_id),))
    inventory_items = cursor.fetchall()
    conn.close()
    return inventory_items

def add_item_to_inventory(user_id, item_id, quantity=1):
    """Adiciona um item ao inventário. Se já existir, aumenta a quantidade."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (str(user_id), item_id))
    result = cursor.fetchone()
    if result:
        new_quantity = result[0] + quantity
        cursor.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, str(user_id), item_id))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", (str(user_id), item_id, quantity))
    conn.commit()
    conn.close()

def remove_item_from_inventory(user_id, item_id, quantity=1):
    """Remove uma quantidade de um item do inventário. Se a quantidade zerar, apaga o registro."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (str(user_id), item_id))
    result = cursor.fetchone()
    if not result or result[0] < quantity:
        conn.close()
        return False
    new_quantity = result[0] - quantity
    if new_quantity > 0:
        cursor.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, str(user_id), item_id))
    else:
        cursor.execute("DELETE FROM inventory WHERE user_id = ? AND item_id = ?", (str(user_id), item_id))
    conn.commit()
    conn.close()
    return True

def get_item_by_name(name):
    """Busca um item pelo seu nome (ignorando maiúsculas/minúsculas)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE LOWER(nome) = ?", (name.lower(),))
    item = cursor.fetchone()
    conn.close()
    return item

def get_all_item_names():
    """Retorna uma lista com os nomes de todos os itens no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM items ORDER BY nome ASC")
    items = [item[0] for item in cursor.fetchall()]
    conn.close()
    return items

def get_all_items_for_listing():
    """Retorna uma lista de todos os itens com nome, tipo e raridade para listagem."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Ordena primeiro por tipo, depois por nome, para facilitar o agrupamento
    cursor.execute("SELECT nome, tipo, raridade FROM items ORDER BY tipo, nome ASC")
    items = cursor.fetchall()
    conn.close()
    return items

def update_player_hp(user_id, amount_to_change):
    """Muda o HP atual do jogador, garantindo que não passe do máximo nem fique abaixo de 0."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pega os dados atuais do jogador para fazer o cálculo
    cursor.execute("SELECT hp, hp_max FROM players WHERE user_id = ?", (str(user_id),))
    player = cursor.fetchone()
    if not player:
        conn.close()
        return None

    # Calcula o novo HP, garantindo que ele fique entre 0 e o HP máximo
    new_hp = player['hp'] + amount_to_change
    new_hp = max(0, min(new_hp, player['hp_max']))

    # Atualiza o banco de dados com o valor correto
    cursor.execute("UPDATE players SET hp = ? WHERE user_id = ?", (new_hp, str(user_id)))
    conn.commit()
    conn.close()
    return new_hp

def update_player_mp(user_id, amount_to_change):
    """Muda o MP atual do jogador, respeitando os limites."""
    player = get_player(user_id)
    if not player: return

    new_mp = player['mp'] + amount_to_change
    new_mp = max(0, min(new_mp, player['mp_max']))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET mp = ? WHERE user_id = ?", (new_mp, str(user_id)))
    conn.commit()
    conn.close()
    return new_mp

def apply_buff(user_id, item_name, stat, amount, duration_minutes):
    """Aplica um buff temporário a um jogador."""
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=duration_minutes)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO active_effects (user_id, item_name, stat, amount, expires_at) VALUES (?, ?, ?, ?, ?)",
        (str(user_id), item_name, stat, amount, expires_at.isoformat())
    )
    conn.commit()
    conn.close()

def get_active_buffs(user_id):
    """Busca todos os buffs ativos para um jogador, removendo os expirados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Remove buffs expirados primeiro
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("DELETE FROM active_effects WHERE user_id = ? AND expires_at < ?", (str(user_id), now_utc))
    
    # Busca os buffs restantes
    cursor.execute("SELECT * FROM active_effects WHERE user_id = ?", (str(user_id),))
    buffs = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return buffs

def equip_item(user_id, item):
    """Equipa um item, devolvendo qualquer item que estava no slot para o inventário."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    slot = item['slot']
    item_id_to_equip = item['item_id']

    # 1. Verifica se já há um item no slot
    cursor.execute(f"SELECT {slot} FROM equipment WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    currently_equipped_id = result[slot] if result else None

    # 2. Se houver, devolve o item antigo para o inventário
    if currently_equipped_id:
        add_item_to_inventory(user_id, currently_equipped_id, 1)

    # 3. Equipa o novo item
    cursor.execute(f"UPDATE equipment SET {slot} = ? WHERE user_id = ?", (item_id_to_equip, str(user_id)))
    
    conn.commit()
    conn.close()

def unequip_item(user_id, slot):
    """Desequipa um item de um slot e o devolve para o inventário."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Pega o ID do item no slot
    cursor.execute(f"SELECT {slot} FROM equipment WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    item_id_to_unequip = result[slot] if result else None

    if not item_id_to_unequip:
        return None # Nada para desequipar

    # 2. Devolve o item para o inventário
    add_item_to_inventory(user_id, item_id_to_unequip, 1)

    # 3. Limpa o slot no equipamento
    cursor.execute(f"UPDATE equipment SET {slot} = NULL WHERE user_id = ?", (str(user_id),))
    
    # Pega o nome do item para a mensagem de confirmação
    cursor.execute("SELECT nome FROM items WHERE item_id = ?", (item_id_to_unequip,))
    item_name = cursor.fetchone()['nome']

    conn.commit()
    conn.close()
    return item_name

def get_player_total_stats(user_id):
    """Calcula os status totais do jogador (base + bônus de equipamentos)."""
    player = get_player(user_id)
    if not player: return None

    total_stats = {
        "forca": player['forca'], "destreza": player['destreza'],
        "inteligencia": player['inteligencia'], "constituicao": player['constituicao'],
        "sorte": player['sorte']
    }
    
    # Pega os IDs dos itens equipados
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE user_id = ?", (str(user_id),))
    equipped_ids_row = cursor.fetchone()

    if equipped_ids_row:
        # Pega os bônus de cada item equipado
        for slot in equipped_ids_row.keys():
            if slot == 'user_id' or not equipped_ids_row[slot]:
                continue
            
            item_id = equipped_ids_row[slot]
            cursor.execute("SELECT bonus_stats FROM items WHERE item_id = ?", (item_id,))
            item_row = cursor.fetchone()

            if item_row and item_row['bonus_stats']:
                bonus = json.loads(item_row['bonus_stats'])
                for stat, value in bonus.items():
                    if stat in total_stats:
                        total_stats[stat] += value
    
    conn.close()
    return total_stats

def get_player_total_stats(user_id):
    """Calcula os status totais do jogador, incluindo ataque e defesa derivados."""
    player = get_player(user_id)
    if not player: return None

    # Começa com os status base do jogador e os de combate zerados
    total_stats = {
        "forca": player['forca'], "destreza": player['destreza'],
        "inteligencia": player['inteligencia'], "constituicao": player['constituicao'],
        "sorte": player['sorte'], "dano": 0, "defesa": 0
    }
    
    STAT_MAP = {
        "for": "forca", "des": "destreza", "int": "inteligencia",
        "con": "constituicao", "sor": "sorte", "dano": "dano", "defesa": "defesa"
    }

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE user_id = ?", (str(user_id),))
    equipped_ids_row = cursor.fetchone()

    if equipped_ids_row:
        for slot in equipped_ids_row.keys():
            if slot == 'user_id' or not equipped_ids_row[slot]:
                continue
            item_id = equipped_ids_row[slot]
            cursor.execute("SELECT bonus_stats FROM items WHERE item_id = ?", (item_id,))
            item_row = cursor.fetchone()
            if item_row and item_row['bonus_stats']:
                bonus = json.loads(item_row['bonus_stats'])
                for short_name, value in bonus.items():
                    full_name = STAT_MAP.get(short_name.lower())
                    if full_name and full_name in total_stats:
                        total_stats[full_name] += value
    
    conn.close()
    
    # Adiciona os cálculos finais de ataque e defesa ao dicionário
    total_stats['ataque_total'] = max(total_stats['forca'], total_stats['destreza']) + total_stats['dano']
    total_stats['defesa_total'] = total_stats['constituicao'] + total_stats['defesa']

    return total_stats

def get_player_equipment_names(user_id):
    """Busca os nomes dos itens equipados por um jogador."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pega os IDs dos itens equipados
    cursor.execute("SELECT * FROM equipment WHERE user_id = ?", (str(user_id),))
    equipped_ids_row = cursor.fetchone()

    equipment_names = {
        'cabeca': None, 'peitoral': None, 'calcas': None,
        'botas': None, 'arma': None, 'acessorio': None
    }

    if equipped_ids_row:
        for slot in equipped_ids_row.keys():
            if slot == 'user_id' or not equipped_ids_row[slot]:
                continue
            
            item_id = equipped_ids_row[slot]
            # Busca o nome do item correspondente ao ID
            cursor.execute("SELECT nome FROM items WHERE item_id = ?", (item_id,))
            item_row = cursor.fetchone()
            if item_row:
                equipment_names[slot] = item_row['nome']
    
    conn.close()
    return equipment_names

def get_random_monster_from_location(location):
    """Busca um monstro aleatório de uma localização específica."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM monsters WHERE localizacao = ? ORDER BY RANDOM() LIMIT 1",
        (location.lower(),)
    )
    monster_data = cursor.fetchone()
    conn.close()
    return monster_data


def grant_rewards(user_id, exp_amount, gold_amount):
    """Adiciona EXP e Ouro a um jogador e lida com múltiplos level ups em um loop."""
    from rpg.game_data import HABILIDADES

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- LÓGICA CORRIGIDA ---

    # 1. PRIMEIRO, LÊ os dados atuais do jogador
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (str(user_id),))
    player_data = cursor.fetchone()
    
    if not player_data:
        conn.close()
        return False

    # 2. SEGUNDO, CALCULA tudo em variáveis Python
    player = dict(player_data) # Cria uma cópia para manipular
    player['exp'] += exp_amount
    player['gold'] += gold_amount
    
    leveled_up = False
    niveis_ganhos = 0
    
    # O loop de level up agora trabalha com as variáveis locais
    while player['exp'] >= player['exp_para_upar']:
        leveled_up = True
        niveis_ganhos += 1
        
        exp_restante = player['exp'] - player['exp_para_upar']
        novo_nivel = player['nivel'] + 1
        nova_exp_para_upar = int(player['exp_para_upar'] * 1.5)
        
        player['exp'] = exp_restante
        player['nivel'] = novo_nivel
        player['exp_para_upar'] = nova_exp_para_upar
        
        # Verifica se aprendeu habilidades
        player_classe = player['classe']
        for skill_key, skill_data in HABILIDADES.items():
            if skill_data['nivel_req'] == novo_nivel and player_classe in skill_data['classes']:
                learn_skill(cursor, user_id, skill_key)

    # 3. TERCEIRO, SALVA o resultado final no banco de dados com um único UPDATE
    if leveled_up:
        bonus_stats = 2 * niveis_ganhos
        bonus_hp_mp = 10 * niveis_ganhos
        
        cursor.execute("""
            UPDATE players 
            SET nivel = ?, exp = ?, exp_para_upar = ?, gold = ?,
            hp_max = hp_max + ?, mp_max = mp_max + ?, 
            forca = forca + ?, destreza = destreza + ?, 
            inteligencia = inteligencia + ?, constituicao = constituicao + ?, 
            sorte = sorte + ?
            WHERE user_id = ?
        """, (
            player['nivel'], player['exp'], player['exp_para_upar'], player['gold'],
            bonus_hp_mp, bonus_hp_mp,
            bonus_stats, bonus_stats, bonus_stats, bonus_stats, bonus_stats,
            str(user_id)
        ))
    else:
        # Se não upou de nível, apenas atualiza a EXP e o Ouro
        cursor.execute(
            "UPDATE players SET exp = ?, gold = ? WHERE user_id = ?",
            (player['exp'], player['gold'], str(user_id))
        )

    conn.commit()
    conn.close()
    return leveled_up

def get_monster_drops(monster_id):
    """Busca a lista de possíveis drops de um monstro."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.item_id, i.nome, md.chance 
        FROM monster_drops md
        JOIN items i ON md.item_id = i.item_id
        WHERE md.monster_id = ?
    """, (monster_id,))
    drops = cursor.fetchall()
    conn.close()
    return drops

def get_monster_by_name(name):
    """Busca os dados de um monstro pelo seu nome."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monsters WHERE nome = ?", (name,))
    monster_data = cursor.fetchone()
    conn.close()
    return monster_data

def learn_skill(cursor, user_id, skill_key):
    """Ensina uma nova habilidade a um jogador usando um cursor existente."""
    # Esta função agora não abre mais sua própria conexão.
    # Ela usa o cursor que recebeu como argumento.
    cursor.execute("INSERT OR IGNORE INTO player_skills (user_id, skill_key) VALUES (?, ?)", (str(user_id), skill_key))

def get_player_skills(user_id):
    """Busca a lista de chaves de habilidades que um jogador conhece."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT skill_key FROM player_skills WHERE user_id = ?", (str(user_id),))
    skills = [row[0] for row in cursor.fetchall()]
    conn.close()
    return skills

def get_equipped_weapon(user_id):
    """Busca os detalhes completos da arma equipada por um jogador."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Primeiro, pega o ID da arma equipada na tabela 'equipment'
    cursor.execute("SELECT arma FROM equipment WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    
    if not result or not result['arma']:
        conn.close()
        return None # Jogador não tem arma equipada

    item_id = result['arma']
    
    # Agora, usa o ID para buscar todos os detalhes do item na tabela 'items'
    cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
    weapon_data = cursor.fetchone()
    
    conn.close()
    return weapon_data

def update_player_mp(user_id, amount_to_change):
    """Muda o MP atual do jogador, respeitando os limites."""
    player = get_player(user_id)
    if not player: return

    new_mp = player['mp'] + amount_to_change
    new_mp = max(0, min(new_mp, player['mp_max']))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET mp = ? WHERE user_id = ?", (new_mp, str(user_id)))
    conn.commit()
    conn.close()
    return new_mp

def apply_buff(user_id, item_name, stat, amount, duration_minutes):
    """Aplica um buff temporário a um jogador."""
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=duration_minutes)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO active_effects (user_id, item_name, stat, amount, expires_at) VALUES (?, ?, ?, ?, ?)",
        (str(user_id), item_name, stat, amount, expires_at.isoformat())
    )
    conn.commit()
    conn.close()

setup_database()