import discord
from discord.ext import commands
import random

class Diversao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anjofull = [
            "É SÓ NO MEU TIME",
            "EU VOU DAR FF",
            "VOU DESINSTALAR ESSE JOGO"
        ]

    @commands.command()
    async def anjo(self, ctx):
        await ctx.send(random.choice(self.anjofull))

    @commands.command()
    async def hevitu(self, ctx):
        porcentagem_boiola = random.randint(0, 100)
        mensagem_resposta = f'Hevitu esta {porcentagem_boiola}% viadinho hoje.'
        await ctx.send(mensagem_resposta)

async def setup(bot):
    await bot.add_cog(Diversao(bot))