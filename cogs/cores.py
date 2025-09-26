# cogs/cores.py
import discord
from discord.ext import commands
from discord.ui import Select, View
import json
import os
from utils import get_server_setting

COLORS_CONFIG_FILE = 'colors.json'

def load_colors():
    if not os.path.exists(COLORS_CONFIG_FILE):
        return []
    with open(COLORS_CONFIG_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_colors(colors_data):
    with open(COLORS_CONFIG_FILE, 'w') as f:
        json.dump(colors_data, f, indent=4)

class ColorView(View):
    def __init__(self):
        super().__init__(timeout=None)
        colors_data = load_colors()
        if not colors_data:
            return

        select_options = [
            discord.SelectOption(
                label=color['label'],
                value=str(color['role_id']),
                emoji=color['emoji']
            ) for color in colors_data
        ]

        self.add_item(
            Select(
                custom_id="color_select_menu",
                placeholder="🎨 Escolha a cor do seu nome!",
                options=select_options
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data['custom_id'] == "color_select_menu":
            await self.handle_color_selection(interaction)
        return False

    async def handle_color_selection(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        member = interaction.user
        selected_role_id = int(interaction.data['values'][0])
        
        colors_data = load_colors()
        all_color_role_ids = {color['role_id'] for color in colors_data}

        roles_to_remove = [role for role in member.roles if role.id in all_color_role_ids]
        new_role = interaction.guild.get_role(selected_role_id)
        
        if not new_role:
            await interaction.followup.send("❌ Ops! O cargo para esta cor não foi encontrado.", ephemeral=True)
            return

        try:
            if new_role in roles_to_remove:
                await member.remove_roles(new_role)
                await interaction.followup.send(f"🎨 Cor {new_role.mention} removida!", ephemeral=True)
            else:
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)
                await member.add_roles(new_role)
                await interaction.followup.send(f"✨ Cor {new_role.mention} aplicada com sucesso!", ephemeral=True)
        except Exception as e:
            print(f"Erro ao gerenciar cargos de cor: {e}")
            await interaction.followup.send("❌ Ocorreu um erro ao aplicar sua cor.", ephemeral=True)


class Cores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ColorView())
        print("Cog de Cores carregado.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcolor(self, ctx, cargo: discord.Role, emoji: str, *, nome: str):
        colors = load_colors()
        if any(c['role_id'] == cargo.id for c in colors):
            await ctx.send(f"❌ O cargo {cargo.mention} já está no sistema de cores.")
            return
        colors.append({"label": nome, "role_id": cargo.id, "emoji": emoji})
        save_colors(colors)
        await ctx.send(f"✅ Cor '{nome}' {emoji} associada ao cargo {cargo.mention} adicionada com sucesso!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removecolor(self, ctx, cargo: discord.Role):
        colors = load_colors()
        original_len = len(colors)
        colors = [c for c in colors if c['role_id'] != cargo.id]
        if len(colors) < original_len:
            save_colors(colors)
            await ctx.send(f"🗑️ O cargo {cargo.mention} foi removido do sistema de cores.")
        else:
            await ctx.send(f"🔎 O cargo {cargo.mention} não foi encontrado no sistema.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def listcolors(self, ctx):
        colors = load_colors()
        if not colors:
            await ctx.send("Nenhuma cor configurada ainda. Use `.addcolor` para começar.")
            return
        embed = discord.Embed(title="🎨 Cores Configuradas no Servidor", color=discord.Color.gold())
        description = ""
        for color in colors:
            role = ctx.guild.get_role(color['role_id'])
            description += f"{color['emoji']} **{color['label']}** - {role.mention if role else 'Cargo não encontrado'}\n"
        embed.description = description
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupcolors(self, ctx):
        canal_configurado_id = get_server_setting(ctx.guild.id, 'cores_channel')

        if not canal_configurado_id:
            await ctx.send("❌ O canal de cores não foi configurado! Use `.setcanal cores #canal`.")
            return

        if ctx.channel.id != canal_configurado_id:
            canal_mencao = self.bot.get_channel(canal_configurado_id).mention
            await ctx.send(f"Este comando só pode ser usado no canal {canal_mencao}.")
            return

        embed = discord.Embed(
            title="🎨 Escolha a Cor do seu Nome!",
            description=(
                "Destaque-se na multidão! Selecione uma das cores abaixo para personalizar como seu nome aparece no servidor.\n\n"
                "Basta clicar no menu e escolher sua cor preferida. Se quiser trocar, é só escolher outra!"
            ),
            color=0xe74c3c
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed, view=ColorView())
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Cores(bot))