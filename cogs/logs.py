import discord
from discord.ext import commands
import datetime
from utils import get_server_setting

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Evento para mensagem apagada
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        log_channel_id = get_server_setting(message.guild.id, 'logs_channel')
        if not log_channel_id:
            return # Se nenhum canal estiver configurado, não faz nada
        
        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return # Se o canal configurado não for encontrado, não faz nada

        embed = discord.Embed(
            title="🗑️ Mensagem Apagada",
            description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        if message.content:
            embed.add_field(name="Conteúdo", value=f"```{message.content}```", inline=False)
        embed.set_footer(text=f"ID do Usuário: {message.author.id}")

        await log_channel.send(embed=embed)

    # mensagem editada
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Ignora bots e verifica se o conteúdo realmente mudou
        if before.author.bot or before.content == after.content:
            return

        log_channel_id = get_server_setting(before.guild.id, 'logs_channel')
        if not log_channel_id:
            return
            
        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return

        embed = discord.Embed(
            title="✏️ Mensagem Editada",
            description=f"**Autor:** {after.author.mention}\n**Canal:** {after.channel.mention}\n[Pular para a Mensagem]({after.jump_url})",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Antes", value=f"```{before.content}```", inline=False)
        embed.add_field(name="Depois", value=f"```{after.content}```", inline=False)
        embed.set_footer(text=f"ID do Usuário: {after.author.id}")

        await log_channel.send(embed=embed)

    # voz (entrar/sair/mudar de canal)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        log_channel_id = get_server_setting(member.guild.id, 'logs_channel')
        if not log_channel_id:
            return
            
        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return

        # Verifica se o usuário ENTROU em um canal de voz
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎙️ Usuário Entrou no Canal de Voz",
                description=f"**Usuário:** {member.mention}\n**Entrou em:** {after.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_footer(text=f"ID do Usuário: {member.id}")
            await log_channel.send(embed=embed)

        if before.channel is not None and after.channel is None:
             embed = discord.Embed(
                 title="🔇 Usuário Saiu do Canal de Voz",
                description=f"**Usuário:** {member.mention}\n**Saiu de:** {before.channel.mention}",
                 color=discord.Color.dark_grey(),
                 timestamp=datetime.datetime.now(datetime.timezone.utc)
             )
             embed.set_footer(text=f"ID do Usuário: {member.id}")
             await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logs(bot))