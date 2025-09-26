# main.py
import discord
from discord.ext import commands
import sys
import os
import asyncio
import traceback

# Adiciona a pasta raiz ao 'path' do Python para encontrar a pasta 'rpg'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from config import TOKEN 

# Configuração inicial do Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Adicionamos help_command=None para desativar o comando de ajuda padrão
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

# Evento que é disparado quando o bot está pronto e conectado
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}!')
    print('------')

# --- NOSSO NOVO GUARDIÃO GLOBAL DE ERROS ---
@bot.event
async def on_command_error(ctx, error):
    """
    Um guardião global que captura qualquer erro de comando no bot.
    """
    # Transforma o erro em uma forma mais legível
    original_error = getattr(error, 'original', error)

    if isinstance(original_error, commands.CommandNotFound):
        # Se o comando simplesmente não existe, não faz nada (evita spam)
        print(f"Comando não encontrado: {ctx.message.content}")
        return
        
    elif isinstance(original_error, commands.CheckFailure):
        # Este é o erro de permissão que estávamos procurando!
        await ctx.send("🔴 **Acesso Negado!** Você não tem permissão para usar este comando.")
        
    elif isinstance(original_error, commands.MissingRequiredArgument):
        # Erro para quando falta um argumento (como em .explorar)
        await ctx.send(f"🤔 Argumentos faltando! Por favor, verifique como o comando deve ser usado. Se precisar, use o comando de ajuda.")
        
    else:
        # Para qualquer outro erro, avisa no chat e imprime o erro completo no console
        await ctx.send("🔴 Ocorreu um erro inesperado ao executar este comando. O desenvolvedor foi notificado.")
        print(f"Erro inesperado no comando '{ctx.command}':")
        # Imprime o traceback completo no console para depuração
        traceback.print_exception(type(original_error), original_error, original_error.__traceback__, file=sys.stderr)

# Função para carregar os Cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f"Falha ao carregar o Cog {filename[:-3]}: {e}")

# Função principal para iniciar o bot
async def main():
    await load_cogs()
    await bot.start(TOKEN)
    
# Ponto de entrada para rodar o bot
if __name__ == "__main__":
    asyncio.run(main())