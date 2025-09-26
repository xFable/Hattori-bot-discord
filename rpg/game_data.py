# rpg/game_data.py

from .definitions import RARIDADES, SLOTS

# --- CATÁLOGO DE AETHELGARD (VERSÃO ZERADA) ---
# Adicione os seus novos itens, monstros, etc., dentro das chaves {} apropriadas.

ITENS_GERAIS = {
# Modelo de Consumível:
# "pocao_cura_fraca": {"nome": "Pocao de Cura Fraca", "tipo": "Consumable", "peso": 0.2, "efeitos": {"on_use": {"effect": "heal", "amount": 50}}},
"pocao_cura_fraca": {"nome": "Poção de Cura Fraca", "tipo": "Consumable", "peso": 0.2, "efeitos": {"on_use": {"effect": "heal", "amount": 50}}},
"pocao_cura_maior": {"nome": "Poção de Cura Maior", "tipo": "Consumable", "peso": 0.5, "raridade": "uncommon", "efeitos": {"on_use": {"effect": "heal", "amount": 200}}},
"pocao_mana": {"nome": "Poção de Mana", "tipo": "Consumable", "peso": 0.4, "raridade": "common", "efeitos": {"on_use": {"effect": "restore_mana", "amount": 120}}},
"antidoto_basico": {"nome": "Antídoto Básico", "tipo": "Consumable", "peso": 0.1, "raridade": "common", "efeitos": {"on_use": {"effect": "cure_status", "status": "poison"}}},
"bomba_de_fumaca": {"nome": "Bomba de Fumaça", "tipo": "Consumable", "peso": 0.6, "raridade": "uncommon", "efeitos": {"on_use": {"effect": "escape", "chance": 0.95}}},
"pergaminho_teleporte": {"nome": "Pergaminho de Teleporte Curto", "tipo": "Consumable", "peso": 0.2, "raridade": "rare", "efeitos": {"on_use": {"effect": "teleport", "range": 15}}},
"pele_de_lobo": {"nome": "Pele de Lobo", "tipo": "Material", "peso": 1.2, "raridade": "common", "efeitos": {}},
"grimoire_ancestral": {"nome": "Grimoire Ancestral", "tipo": "Livro", "peso": 2.5, "raridade": "epic", "efeitos": {"on_equip": {"effect": "spell_power", "amount": 10}}},
}


ARMAS = {
# Modelo de Arma:
# "adaga_de_ferro": {"nome": "Adaga de Ferro", "tipo": "Adaga", "peso": 1.2, "raridade": "common", "slot": "weapon", "stats": {"dano": 12, "des": 2}, "efeitos": {"on_hit": {"type": "status", "status": "bleed", "chance": 0.1, "duration": 2}}},
"adaga_de_ferro": {"nome": "Adaga de Ferro", "tipo": "Adaga", "peso": 1.2, "raridade": "common", "slot": "weapon", "stats": {"dano": 12, "des": 2}, "efeitos": {"on_hit": {"type": "status", "status": "bleed", "chance": 0.1, "duration": 2}}},
"espada_longa_de_prata": {"nome": "Espada Longa de Prata", "tipo": "Espada", "peso": 3.5, "raridade": "uncommon", "slot": "weapon", "stats": {"dano": 28, "for": 3}, "efeitos": {"on_hit": {"type": "status", "status": "bane", "chance": 0.12, "duration": 3}}},
"machado_do_berserker": {"nome": "Machado do Berserker", "tipo": "Machado", "peso": 6.5, "raridade": "rare", "slot": "weapon", "stats": {"dano": 40, "for": 5}, "efeitos": {"on_hit": {"type": "status", "status": "bleed", "chance": 0.2, "duration": 3}, "on_kill": {"effect": "temporary_buff", "stat": "dano", "amount": 10, "duration": 5}}},
"katana_do_viajante": {"nome": "Katana do Viajante", "tipo": "Katana", "peso": 2.8, "raridade": "uncommon", "slot": "weapon", "stats": {"dano": 25, "des": 4}, "efeitos": {"on_crit": {"type": "status", "status": "bleed", "chance": 0.25, "duration": 4}}},
"arco_curvo_elfico": {"nome": "Arco Curvo Élfico", "tipo": "Arco", "peso": 2.2, "raridade": "rare", "slot": "weapon", "stats": {"dano": 22, "des": 3}, "efeitos": {"on_hit": {"type": "status", "status": "slow", "chance": 0.15, "duration": 2}}},
"cajado_etereo": {"nome": "Cajado Etéreo", "tipo": "Cajado", "peso": 3.0, "raridade": "epic", "slot": "weapon", "stats": {"dano": 18, "int": 6}, "efeitos": {"on_hit": {"type": "status", "status": "mana_burn", "chance": 0.2, "amount": 30}}},
"martelo_do_trovao": {"nome": "Martelo do Trovão", "tipo": "Martelo", "peso": 8.0, "raridade": "legendary", "slot": "weapon", "stats": {"dano": 45, "for": 6}, "efeitos": {"on_hit": {"type": "status", "status": "stun", "chance": 0.15, "duration": 2}}},
}


ARMADURAS = {
# Modelo de Armadura:
# "elmo_de_couro": {"nome": "Elmo de Couro", "tipo": "Leve", "peso": 2.0, "raridade": "common", "slot": "head", "stats": {"defesa": 10, "con": 2}},
"elmo_de_couro": {"nome": "Elmo de Couro", "tipo": "Leve", "peso": 2.0, "raridade": "common", "slot": "head", "stats": {"defesa": 10, "con": 2}},
"cota_de_couro_acinzentado": {"nome": "Cota de Couro Acinzentado", "tipo": "Leve", "peso": 6.0, "raridade": "common", "slot": "chest", "stats": {"defesa": 18, "con": 1}},
"couracao_de_aco": {"nome": "Couraça de Aço", "tipo": "Pesada", "peso": 12.0, "raridade": "uncommon", "slot": "chest", "stats": {"defesa": 40, "for": 3}},
"botas_de_furtividade": {"nome": "Botas de Furtividade", "tipo": "Leve", "peso": 1.0, "raridade": "rare", "slot": "feet", "stats": {"defesa": 5, "des": 4}, "efeitos": {"passive": {"effect": "stealth", "amount": 12}}},
"grevas_do_guardiao": {"nome": "Grevas do Guardião", "tipo": "Pesada", "peso": 4.0, "raridade": "uncommon", "slot": "legs", "stats": {"defesa": 22, "con": 3}},
"capa_da_nevoa": {"nome": "Capa da Névoa", "tipo": "Tecido", "peso": 0.8, "raridade": "rare", "slot": "back", "stats": {"defesa": 6}, "efeitos": {"passive": {"effect": "evasion", "amount": 8}}},
}


ESCUDOS = {
"escudo_redondo_de_ferro": {"nome": "Escudo Redondo de Ferro", "tipo": "Escudo", "peso": 6.0, "raridade": "common", "slot": "shield", "stats": {"defesa": 20, "for": 1}, "efeitos": {"on_block": {"effect": "stagger", "chance": 0.05, "duration": 1}}},
"escudo_torre_de_carvalho": {"nome": "Escudo Torre de Carvalho", "tipo": "Escudo", "peso": 10.0, "raridade": "uncommon", "slot": "shield", "stats": {"defesa": 35, "con": 2}, "efeitos": {"on_block": {"effect": "damage_reduction", "amount": 0.2}}},
}


ACESSORIOS = {
"anel_do_vigor": {"nome": "Anel do Vigor", "tipo": "Anel", "peso": 0.1, "raridade": "rare", "slot": "ring", "stats": {"con": 5, "for": 2}, "efeitos": {"passive": {"effect": "stamina_regen", "amount": 2}}},
"anel_da_vida": {"nome": "Anel da Vida", "tipo": "Anel", "peso": 0.1, "raridade": "rare", "slot": "ring", "stats": {"con": 4}, "efeitos": {"passive": {"effect": "hp_regen", "amount": 3}}},
"anel_da_forca": {"nome": "Anel da Força", "tipo": "Anel", "peso": 0.1, "raridade": "uncommon", "slot": "ring", "stats": {"for": 3}, "efeitos": {"passive": {"effect": "melee_damage", "amount": 5}}},
"amuleto_do_sabio": {"nome": "Amuleto do Sábio", "tipo": "Amuleto", "peso": 0.3, "raridade": "rare", "slot": "necklace", "stats": {"int": 6, "sab": 4}, "efeitos": {"passive": {"effect": "mana_regen", "amount": 3}}},
"amuleto_da_mente": {"nome": "Amuleto da Mente", "tipo": "Amuleto", "peso": 0.2, "raridade": "uncommon", "slot": "necklace", "stats": {"int": 4}, "efeitos": {"passive": {"effect": "spell_crit", "amount": 0.05}}},
"colar_da_sorte_do_aventureiro": {"nome": "Colar da Sorte do Aventureiro", "tipo": "Colar", "peso": 0.2, "raridade": "uncommon", "slot": "necklace", "stats": {"sorte": 5}, "efeitos": {"passive": {"effect": "loot_boost", "chance": 0.1}}},
}

# --- BESTIÁRIO ---
MONSTROS = {
    # Chave interna: (Nome de exibição, HP, Ataque, Defesa, EXP, Gold, Localização)
    "goblin_recruta": ('Goblin Recruta', 50, 10, 5, 10, 5, 'floresta'),
}

BOSSES = {
    # "rei_goblin": ('Rei Goblin', 300, 35, 20, 200, 150, 'floresta'),
}

# --- GRIMÓRIO DE HABILIDADES ---
HABILIDADES = {
    "golpe_poderoso": {"nome": "Golpe Poderoso", "descricao": "Um ataque devastador que consome MP para causar dano extra.", "custo_mp": 15, "tipo": "Dano", "dano_base": 10, "escala_atributo": "forca", "multiplicador": 1.5, "classes": ["Guerreiro", "Paladino"], "nivel_req": 2},
    "bola_de_fogo": {"nome": "Bola de Fogo", "descricao": "Lança uma esfera de fogo...", "custo_mp": 20, "tipo": "Dano", "dano_base": 25, "escala_atributo": "inteligencia", "multiplicador": 1.8, "classes": ["Mago", "Elementalista"], "nivel_req": 1},
}

# --- TABELA DE DROPS ---
DROP_TABLES = {
    # Use as chaves internas dos monstros e itens para definir os drops
    "goblin_recruta": [
        # {"item_key": "pocao_cura_fraca", "chance": 50.0},
    ],
}