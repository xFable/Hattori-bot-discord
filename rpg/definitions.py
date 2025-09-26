# rpg/definitions.py

# --- DEFINIÇÕES DE DADOS FIXOS DO JOGO ---

RARIDADES = {
    "common": "⚪ Comum",
    "uncommon": "🟢 Incomum",
    "rare": "🔵 Raro",
    "epic": "🟣 Epico",
    "legendary": "🟠 Lendario"
}

SLOTS = {
    "weapon": "Arma",
    "shield": "Escudo",
    "head": "Cabeca",
    "chest": "Peitoral",
    "legs": "Calcas",
    "feet": "Botas",
    "hands": "Luvas",
    "ring": "Anel",
    "amulet": "Amuleto",
    "cloak": "Capa",
    "none": "Nenhum" # Para consumíveis e materiais
}

CLASSES_BASE = {
    "Guerreiro": {"for": 15, "des": 8, "int": 5, "con": 12, "sor": 10, "emoji": "⚔️"},
    "Mago": {"for": 5, "des": 8, "int": 15, "con": 10, "sor": 12, "emoji": "🔮"},
    "Arqueiro": {"for": 8, "des": 15, "int": 7, "con": 10, "sor": 10, "emoji": "🏹"},
    "Ladino": {"for": 10, "des": 15, "int": 5, "con": 8, "sor": 12, "emoji": "🗡️"},
    "Paladino": {"for": 13, "des": 7, "int": 10, "con": 12, "sor": 8, "emoji": "🛡️"},
    "Clérigo": {"for": 8, "des": 7, "int": 13, "con": 12, "sor": 10, "emoji": "⚕️"},
    "Necromante": {"for": 5, "des": 8, "int": 16, "con": 9, "sor": 12, "emoji": "💀"},
    "Druida": {"for": 7, "des": 10, "int": 12, "con": 11, "sor": 10, "emoji": "🌳"},
    "Elementalista": {"for": 4, "des": 9, "int": 17, "con": 8, "sor": 12, "emoji": "🔥"},
    "Assassino": {"for": 8, "des": 17, "int": 5, "con": 7, "sor": 13, "emoji": "🔪"}
}

RACAS_BONUS = {
    "Humano": {"for": 1, "des": 1, "int": 1, "con": 1, "sor": 1, "emoji": "🧑"},
    "Elfo": {"for": 0, "des": 2, "int": 1, "con": 0, "sor": 0, "emoji": "🧝"},
    "Anão": {"for": 1, "des": 0, "int": 0, "con": 2, "sor": 0, "emoji": "🧔"},
    "Orc": {"for": 3, "des": 0, "int": -1, "con": 1, "sor": 0, "emoji": "👹"},
    "Dragão": {"for": 2, "des": -1, "int": 2, "con": 1, "sor": 0, "emoji": "🐲"},
    "Gigante": {"for": 4, "des": -2, "int": -2, "con": 3, "sor": 0, "emoji": "🗿"},
    "Minotauro": {"for": 3, "des": 1, "int": -2, "con": 2, "sor": -1, "emoji": "🐂"},
    "Vampiro": {"for": 0, "des": 2, "int": 2, "con": -1, "sor": 1, "emoji": "🧛"},
    "Lobisomem": {"for": 2, "des": 2, "con": 1, "int": -2, "sor": 1, "emoji": "🐺"},
    "Zumbi": {"for": 1, "des": -3, "int": -3, "con": 5, "sor": -2, "emoji": "🧟"}
}

def calcular_stats_iniciais(raca, classe):
    """Calcula os atributos finais somando os bônus de raça e classe."""
    if raca not in RACAS_BONUS or classe not in CLASSES_BASE:
        raise ValueError("Raça ou Classe inválida.")

    base = CLASSES_BASE[classe]
    bonus = RACAS_BONUS[raca]
    
    final_stats = {
        "for": base["for"] + bonus["for"],
        "des": base["des"] + bonus["des"],
        "int": base["int"] + bonus["int"],
        "con": base["con"] + bonus["con"],
        "sor": base["sor"] + bonus["sor"],
    }
    
    final_stats["hp"] = 100 + (final_stats["con"] * 10)
    final_stats["mp"] = 50 + (final_stats["int"] * 5)
    
    return final_stats