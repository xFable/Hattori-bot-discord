# cogs/rpg_combat.py
import discord
from discord.ext import commands
import asyncio
import random
from discord import ui
from rpg import database
from rpg.location_data import LOCATIONS
# Importa a nossa View do novo arquivo
from ._rpg_combat_view import CombatView

# cogs/rpg_combat.py

# ... (os imports e as classes CombatView e ItemSelect devem estar acima, como antes)

class RPGCombat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _handle_exploration(self, source, author, location_key):
        """Função central que gerencia todos os eventos de exploração."""
        channel = source.channel

        loc_data = LOCATIONS.get(location_key.lower())
        if not loc_data:
            await channel.send("Um caminho misterioso te levou a lugar nenhum...")
            return

        await channel.send(f"🔎 Você começa a explorar a **{loc_data['nome_exibicao']}**...")
        await asyncio.sleep(2)

        eventos = loc_data['eventos']
        pesos = [evento['weight'] for evento in eventos]
        evento_sorteado = random.choices(eventos, weights=pesos, k=1)[0]
        
        # --- PROCESSAMENTO DO EVENTO ---
        if evento_sorteado['type'] == 'combat':
            await channel.send(f"📍 **{loc_data['nome_exibicao']}**\n{evento_sorteado['description']}")
            await asyncio.sleep(1.5)
            
            monster_name = random.choice(evento_sorteado['data']['monsters'])
            monster = database.get_monster_by_name(monster_name)
            if not monster:
                await channel.send("Erro: monstro não encontrado no DB.")
                return

            # A variável 'player' é definida aqui, dentro do 'if'
            player = database.get_player(author.id)
            database.update_player_hp(player['user_id'], player['hp_max'])
            player = database.get_player(author.id)
            
            # A 'CombatView' é criada aqui, usando as variáveis 'player' e 'monster'
            # que acabamos de criar.
            view = CombatView(self, author, player, monster)
            embed = discord.Embed(title=f"⚔️ Batalha Iminente!", color=discord.Color.light_grey())
            embed.add_field(name="Sua Vida ❤️", value=f"{view.player_hp} / {view.player_data['hp_max']}", inline=True)
            embed.add_field(name=f"Vida do {view.monster_data['nome']} 👹", value=f"{view.monster_hp} / {view.monster_data['hp_max']}", inline=True)
            
            message = await channel.send(embed=embed, view=view)
            view.message = message

        elif evento_sorteado['type'] == 'loot':
            recompensas = []
            if 'gold' in evento_sorteado['data']:
                gold = evento_sorteado['data']['gold']
                database.grant_rewards(author.id, 0, gold)
                recompensas.append(f"💰 {gold} Ouro")
            
            if 'items' in evento_sorteado['data']:
                for item_info in evento_sorteado['data']['items']:
                    item = database.get_item_by_name(item_info['nome'])
                    if item:
                        database.add_item_to_inventory(author.id, item['item_id'], item_info['quantidade'])
                        recompensas.append(f"✅ {item_info['quantidade']}x {item_info['nome']}")

            embed = discord.Embed(title="💎 Tesouro Encontrado! 💎", color=discord.Color.gold())
            embed.description = f"📍 **{loc_data['nome_exibicao']}**\n{evento_sorteado['description']}\n\n**Você obteve:**\n" + "\n".join(recompensas)
            await channel.send(embed=embed)

        elif evento_sorteado['type'] == 'choice':
            view = ui.View(timeout=180)
            
            async def choice_callback(interaction: discord.Interaction):
                if interaction.user.id != author.id:
                    await interaction.response.send_message("Esta escolha não é sua!", ephemeral=True)
                    return
                
                for child in view.children:
                    child.disabled = True
                await interaction.message.edit(view=view)
                
                await interaction.response.defer()
                next_location_key = interaction.data["custom_id"]
                await self._handle_exploration(interaction, author, next_location_key)

            for key, label in evento_sorteado['data']['options'].items():
                button = ui.Button(label=label, style=discord.ButtonStyle.primary, custom_id=key)
                button.callback = choice_callback
                view.add_item(button)

            # Para responder a uma interação ou a um comando
            if isinstance(source, discord.Interaction):
                await source.followup.send(f"📍 **{loc_data['nome_exibicao']}**\n{evento_sorteado['description']}\n\n*{evento_sorteado['data']['prompt']}*", view=view)
            else:
                await channel.send(f"📍 **{loc_data['nome_exibicao']}**\n{evento_sorteado['description']}\n\n*{evento_sorteado['data']['prompt']}*", view=view)

    @commands.command(name="explorar")
    async def explorar(self, ctx, localizacao: str, debug_mode: str = None):
        """Explora uma área. Adicione 'debug' no final para depurar."""
        # Lógica do modo de depuração que já criamos
        if debug_mode and debug_mode.lower() == 'debug':
            # ... (código do debug mode) ...
            return
        
        # Execução normal
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Crie um personagem com `.iniciar` primeiro.")
            return
        
        await self._handle_exploration(ctx, ctx.author, localizacao)

    @explorar.error
    async def explorar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("🤔 Onde você quer explorar?\n\n"
                           "**Uso correto:** `.explorar <localizacao>`\n"
                           "**Locais disponíveis no momento:** `floresta`, `Caverna`, `Pantano`")
        else:
            await ctx.send("🔴 Ocorreu um erro inesperado ao tentar explorar.")
            print(f"Erro no comando 'explorar': {error}")

async def setup(bot):
    await bot.add_cog(RPGCombat(bot))