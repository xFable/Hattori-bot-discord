# cogs/registro.py
import discord
from discord.ext import commands
from discord.ui import Select, View, Button, select, button
from utils import get_server_setting

class RegistroView(View):
    def __init__(self, user_selections_dict, role_ids: dict):
        super().__init__(timeout=None)
        self.user_selections = user_selections_dict
        self.role_ids = role_ids

        # --- MENU DE SELEÇÃO: IDADE ---
        self.add_item(Select(
            custom_id="select_idade",
            placeholder="🎂 Selecione sua faixa etária",
            options=[
                discord.SelectOption(label="Menor de 18 anos", value=str(self.role_ids['menor_18'])),
                discord.SelectOption(label="18 anos ou mais", value=str(self.role_ids['maior_18']))
            ]
        ))
        
        # --- MENU DE SELEÇÃO: GÊNERO ---
        self.add_item(Select(
            custom_id="select_genero",
            placeholder="👤 Selecione seu gênero",
            options=[
                discord.SelectOption(label="Masculino", value=str(self.role_ids['masculino'])),
                discord.SelectOption(label="Feminino", value=str(self.role_ids['feminino']))
            ]
        ))

        # --- MENU DE SELEÇÃO: COR ---
        self.add_item(Select(
            custom_id="select_cor",
            placeholder="🎨 Selecione sua cor preferida",
            options=[
                discord.SelectOption(label="Azul", value=str(self.role_ids['azul'])),
                discord.SelectOption(label="Preto", value=str(self.role_ids['preto'])),
                discord.SelectOption(label="Branco", value=str(self.role_ids['branco']))
            ]
        ))
    
    @select(custom_id="select_idade")
    async def select_idade_callback(self, interaction: discord.Interaction, select: Select):
        if interaction.user.id not in self.user_selections:
            self.user_selections[interaction.user.id] = {}
        self.user_selections[interaction.user.id]['idade'] = select.values[0]
        await interaction.response.defer()

    @select(custom_id="select_genero")
    async def select_genero_callback(self, interaction: discord.Interaction, select: Select):
        if interaction.user.id not in self.user_selections:
            self.user_selections[interaction.user.id] = {}
        self.user_selections[interaction.user.id]['genero'] = select.values[0]
        await interaction.response.defer()

    @select(custom_id="select_cor")
    async def select_cor_callback(self, interaction: discord.Interaction, select: Select):
        if interaction.user.id not in self.user_selections:
            self.user_selections[interaction.user.id] = {}
        self.user_selections[interaction.user.id]['cor'] = select.values[0]
        await interaction.response.defer()
        
    @button(label="Confirmar Registro", style=discord.ButtonStyle.green, custom_id="confirm_button", emoji="✅")
    async def confirm_button_callback(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        
        if user_id not in self.user_selections or len(self.user_selections[user_id]) < 3:
            await interaction.response.send_message("❌ **Ops!** Você precisa selecionar uma opção em cada um dos 3 menus antes de confirmar!", ephemeral=True)
            return

        try:
            member = interaction.user
            cargos_a_add = [
                interaction.guild.get_role(int(self.user_selections[user_id]['idade'])),
                interaction.guild.get_role(int(self.user_selections[user_id]['genero'])),
                interaction.guild.get_role(int(self.user_selections[user_id]['cor']))
            ]
            
            await member.add_roles(*cargos_a_add)
            
            del self.user_selections[user_id]
            
            await interaction.response.send_message("🎉 **Prontinho!** Seus cargos foram atribuídos com sucesso. Bem-vindo(a)!", ephemeral=True)
        
        except Exception as e:
            print(f"Erro ao atribuir cargos: {e}")
            await interaction.response.send_message("Ocorreu um erro ao tentar atribuir seus cargos. Por favor, contate um administrador.", ephemeral=True)

class Registro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_selections = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog de Registro carregado.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild_id_str = str(ctx.guild.id)
        settings = get_server_setting(guild_id_str, None)
        if not settings:
            await ctx.send("❌ Nenhuma configuração encontrada. Use `.statusregistro` para ver o que falta.")
            return

        canal_configurado_id = settings.get('registro_channel')
        if not canal_configurado_id or ctx.channel.id != canal_configurado_id:
            await ctx.send(f"Este comando só pode ser usado no canal de registro. Use `.statusregistro` para verificar.")
            return
        
        cargos_configurados = settings.get('registro_roles', {})
        tipos_necessarios = ["menor_18", "maior_18", "masculino", "feminino", "azul", "preto", "branco"]
        
        if not all(key in cargos_configurados for key in tipos_necessarios):
            await ctx.send("❌ Nem todos os cargos de registro foram configurados! Use `.statusregistro` para ver quais faltam.")
            return
            
        view = RegistroView(self.user_selections, cargos_configurados)
        
        embed = discord.Embed(
            title="✨ Bem-vindo(a) ao nosso Sistema de Registro! ✨",
            description=(
                "Para uma melhor experiência em nosso servidor, pedimos que você personalize seu perfil.\n\n"
                "**Como funciona?**\n"
                "1️⃣ **Selecione** suas preferências nos 3 menus abaixo.\n"
                "2️⃣ **Clique** no botão verde `Confirmar Registro`.\n"
                "3️⃣ **Pronto!** Você receberá seus cargos automaticamente.\n\n"
                "*Isso nos ajuda a entender melhor nossa comunidade!*"
            ),
            color=discord.Color.from_rgb(88, 101, 242)
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(text=f"Painel de registro do servidor {ctx.guild.name}")
        
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Registro(bot))