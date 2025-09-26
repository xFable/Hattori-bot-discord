# verificar.py
# Coloque este arquivo na sua pasta principal (HATTORI/)

# Adicionamos o caminho para que o script consiga encontrar a pasta 'rpg'
import sys
sys.path.append('.')

from collections import Counter

print("--- Iniciando verificação final de NOMES duplicados (case-insensitive) ---")

try:
    # Tenta importar os dados do seu novo catálogo de itens
    from rpg.game_data import ITENS_GERAIS, ARMAS, ARMADURAS, ESCUDOS, ACESSORIOS
except ImportError:
    print("\n!!! ERRO !!!")
    print("Não consegui encontrar o arquivo 'rpg/game_data.py' ou as listas de itens dentro dele.")
    print("Certifique-se de que o arquivo existe e que as listas de dicionários (ITENS_GERAIS, ARMAS, etc.) estão nele.")
    exit()

# Lista com todos os dicionários de itens
todas_as_listas = [ITENS_GERAIS, ARMAS, ARMADURAS, ESCUDOS, ACESSORIOS]
todos_os_nomes = []

# Itera sobre cada dicionário e coleta todos os nomes
for dicionario in todas_as_listas:
    for item_data in dicionario.values():
        nome = item_data.get("nome")
        if nome:
            # Limpa o nome (minúsculas, sem espaços extras) para uma comparação justa
            todos_os_nomes.append(nome.lower().strip())

# Conta a ocorrência de cada nome
contagem = Counter(todos_os_nomes)

# Filtra para mostrar apenas os nomes que aparecem mais de uma vez
duplicados = {nome: num for nome, num in contagem.items() if num > 1}

if duplicados:
    print("\n!!! DUPLICATAS ENCONTRADAS !!!")
    print("Os seguintes NOMES de itens estão repetidos em suas listas:")
    for nome, num in duplicados.items():
        print(f"- '{nome.title()}' (aparece {num} vezes)")
    print("\nAbra o arquivo 'rpg/game_data.py' e corrija estas entradas para que cada item tenha um nome único.")
else:
    print("\n✅ Verificação concluída. Nenhuma duplicata de nome encontrada.")
    print("Se a contagem de itens no 'popular_mundo.py' ainda estiver errada, o mistério é ainda maior.")
    
print("\n--- Verificação finalizada ---")