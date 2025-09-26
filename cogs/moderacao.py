import discord
from discord.ext import commands

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True) 
    async def limpar(self, ctx, quantidade: int = 50):
        try:
            deleted = await ctx.channel.purge(limit=quantidade + 1) 
            await ctx.send(f'🧹 Limpei {len(deleted) - 1} mensagens!', delete_after=5)
        except discord.Forbidden:
            await ctx.send("Eu não tenho permissão para apagar mensagens neste canal!", ephemeral=True)
        except commands.MissingPermissions:
            await ctx.send("Você não tem permissão para usar este comando!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacao(bot))