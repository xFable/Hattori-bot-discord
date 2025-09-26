import discord
from discord.ext import commands
from utils import set_server_setting, get_server_setting, load_settings, save_settings

# Lista dos tipos de cargos que nosso sistema de registro precisa
TIPOS_DE_CARGO_REGISTRO = [
    "menor_18", "maior_18", "masculino", "feminino", "azul", "preto", "branco"
]

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setcanal(self, ctx, tipo: str, canal: discord.TextChannel):
        """
        Define o canal para uma função específica.
        Uso: .setcanal [registro|cores|logs] #nome-do-canal
        """
        tipo = tipo.lower()
        
        if tipo not in ['registro', 'cores', 'logs']:
            await ctx.send("❌ Tipo inválido! Use 'registro', 'cores' ou 'logs'.")
            return
            
        config_key = f"{tipo}_channel"
        set_server_setting(ctx.guild.id, config_key, canal.id)
        
        await ctx.send(f"✅ O canal de **{tipo}** foi definido para {canal.mention} com sucesso!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setcargo(self, ctx, tipo_cargo: str, cargo: discord.Role):
        """
        Define um cargo para uma função do registro.
        Uso: .setcargo [tipo] @cargo
        Tipos: menor_18, maior_18, masculino, feminino, azul, preto, branco
        """
        tipo_cargo = tipo_cargo.lower()
        
        if tipo_cargo not in TIPOS_DE_CARGO_REGISTRO:
            tipos_validos = ", ".join(TIPOS_DE_CARGO_REGISTRO)
            await ctx.send(f"❌ Tipo de cargo inválido! Use um dos seguintes: `{tipos_validos}`")
            return

        settings = load_settings()
        guild_id = str(ctx.guild.id)

        if guild_id not in settings:
            settings[guild_id] = {}
        if "registro_roles" not in settings[guild_id]:
            settings[guild_id]["registro_roles"] = {}
        
        settings[guild_id]["registro_roles"][tipo_cargo] = cargo.id
        save_settings(settings)
        
        await ctx.send(f"✅ O cargo para **{tipo_cargo}** foi definido como {cargo.mention}!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def statusregistro(self, ctx):
        """Mostra o status da configuração do sistema de registro."""
        guild_id = str(ctx.guild.id)
        settings = load_settings().get(guild_id, {})
        
        embed = discord.Embed(
            title="✅ Status da Configuração do Registro", 
            color=discord.Color.blue()
        )
        
        canal_id = settings.get('registro_channel')
        if canal_id and (canal := self.bot.get_channel(canal_id)):
            embed.add_field(name="Canal de Registro", value=f"✅ {canal.mention}", inline=False)
        else:
            embed.add_field(name="Canal de Registro", value="❌ Não configurado (`.setcanal registro #canal`)", inline=False)
            
        cargos_config = settings.get('registro_roles', {})
        status_cargos = ""
        todos_configurados = True
        for tipo in TIPOS_DE_CARGO_REGISTRO:
            cargo_id = cargos_config.get(tipo)
            if cargo_id and (cargo := ctx.guild.get_role(cargo_id)):
                status_cargos += f"✅ **{tipo}**: {cargo.mention}\n"
            else:
                status_cargos += f"❌ **{tipo}**: Não configurado (`.setcargo {tipo} @cargo`)\n"
                todos_configurados = False

        embed.add_field(name="Cargos de Registro", value=status_cargos, inline=False)

        if todos_configurados and canal_id:
             embed.set_footer(text="Tudo pronto! Você já pode usar o comando .setup no canal de registro.")
        else:
             embed.set_footer(text="Configure os itens pendentes (❌) para poder usar o comando .setup.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Config(bot))