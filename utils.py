# utils.py
import json
import os

SETTINGS_FILE = 'settings.json'

def load_settings():
    """Carrega as configurações do arquivo JSON."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Se o arquivo estiver corrompido ou vazio, retorna um dicionário vazio
        return {}

def save_settings(settings):
    """Salva as configurações no arquivo JSON."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def get_server_setting(guild_id, key):
    """Busca uma configuração específica para um servidor. Se a key for None, retorna todas as configs."""
    settings = load_settings()
    guild_settings = settings.get(str(guild_id), {})
    
    if key is None:
        return guild_settings
        
    return guild_settings.get(key)

def set_server_setting(guild_id, key, value):
    """Define uma configuração específica para um servidor."""
    settings = load_settings()
    guild_id_str = str(guild_id)
    
    # Garante que o dicionário para o servidor existe
    if guild_id_str not in settings:
        settings[guild_id_str] = {}
        
    settings[guild_id_str][key] = value
    save_settings(settings)