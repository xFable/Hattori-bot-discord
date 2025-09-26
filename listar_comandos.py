import discord
from discord.ext import commands
import os
import sys
import asyncio
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

async def listar_todos_os_comandos():
    """
    Carrega todos os cogs de forma assíncrona, inspeciona o bot 
    e gera uma lista formatada.
    """
    print("Iniciando a busca por comandos...")

    try:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
        print(f"-> {len(bot.cogs)} Cogs carregados com sucesso.")
    except Exception as e:
        print(f"ERRO: Falha ao carregar um Cog. Verifique seus arquivos. Erro: {e}")
        return None

    comandos_por_cog = defaultdict(list)
    for comando in sorted(bot.commands, key=lambda c: c.name):
        if comando.hidden:
            continue
        categoria = comando.cog_name or "Geral"
        comandos_por_cog[categoria].append(comando)

    output_text = " HATTORI BOT - LISTA DE COMANDOS \n"
    output_text += "=" * 40 + "\n\n"

    for categoria, lista_comandos in comandos_por_cog.items():
        output_text += f"--- {categoria.upper()} ---\n"
        for comando in lista_comandos:
            output_text += f"  {bot.command_prefix}{comando.name}"
            if comando.signature:
                output_text += f" {comando.signature}\n"
            else:
                output_text += "\n"
            
            docstring = comando.help or "Sem descrição."
            output_text += f"    -> {docstring.strip()}\n"

            if comando.aliases:
                aliases_formatados = ', '.join([f"{bot.command_prefix}{alias}" for alias in comando.aliases])
                output_text += f"    (Apelidos: {aliases_formatados})\n"
            
            output_text += "\n"
        output_text += "\n"

    return output_text

# --- Script de forma assíncrona ---
async def main():
    """Função principal para rodar a listagem e fechar o bot."""
    lista_formatada = await listar_todos_os_comandos()
    
    if lista_formatada:
        print("\n" + "="*40)
        print(lista_formatada)
        print("="*40)
        
        try:
            with open("comandos.txt", "w", encoding="utf-8") as f:
                f.write(lista_formatada)
            print("\n✅ Lista de comandos também foi salva no arquivo 'comandos.txt'!")
        except Exception as e:
            print(f"\nERRO: Não foi possível salvar o arquivo. Erro: {e}")

    await bot.close()

if __name__ == "__main__":
    asyncio.run(main())