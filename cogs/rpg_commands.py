# cogs/rpg_commands.py
import discord
from discord.ext import commands
from discord import ui
import datetime
import json
from rpg import database
from rpg.definitions import CLASSES_BASE, RACAS_BONUS, calcular_stats_iniciais, SLOTS, RARIDADES

# Modal para o usuário inserir o nome do personagem
class NameInputModal(ui.Modal, title="Qual o nome do seu aventureiro?"):
    nome = ui.TextInput(label="Nome do Personagem", placeholder="Ex: Kael, o Valente", required=True, max_length=50)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

# View principal para a criação do personagem
class CharacterCreationView(ui.View):
    def __init__(self, author):
        super().__init__(timeout=300)
        self.author = author
        self.raca = None
        self.classe = None
        self.nome = None

    @ui.select(placeholder="1. Escolha sua Raça...", options=[
        discord.SelectOption(label=raca, emoji=data['emoji']) for raca, data in RACAS_BONUS.items()
    ])
    async def select_raca(self, interaction: discord.Interaction, select: ui.Select):
        self.raca = select.values[0]
        await interaction.response.send_message(f"Você escolheu a raça **{self.raca}**! Agora, escolha sua classe.", ephemeral=True)

    @ui.select(placeholder="2. Escolha sua Classe...", options=[
        discord.SelectOption(label=classe, emoji=data['emoji']) for classe, data in CLASSES_BASE.items()
    ])
    async def select_classe(self, interaction: discord.Interaction, select: ui.Select):
        self.classe = select.values[0]
        await interaction.response.send_message(f"Você escolheu a classe **{self.classe}**! Agora, clique para definir seu nome.", ephemeral=True)
    
    @ui.button(label="3. Definir Nome e Finalizar", style=discord.ButtonStyle.green)
    async def finalize_button(self, interaction: discord.Interaction, button: ui.Button):
        if not self.raca or not self.classe:
            await interaction.response.send_message("Você precisa escolher uma raça e uma classe antes de finalizar!", ephemeral=True)
            return
        
        modal = NameInputModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.nome = modal.nome.value
        self.stop()

class RPGCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="iniciar")
    async def iniciar(self, ctx):
        """Inicia sua aventura em Aethelgard e cria seu personagem."""
        if database.get_player(ctx.author.id):
            await ctx.send(f"⚔️ **{ctx.author.name}**, você já iniciou sua jornada!")
            return

        embed = discord.Embed(
            title="✨ Criação de Personagem em Aethelgard ✨",
            description="Siga os passos abaixo para forjar seu herói. Use os menus de seleção para escolher sua raça e classe, e então clique no botão para definir seu nome e começar sua aventura!",
            color=discord.Color.dark_gold()
        )
        view = CharacterCreationView(ctx.author)
        message = await ctx.send(embed=embed, view=view)

        await view.wait()
        
        if view.raca and view.classe and view.nome:
            stats = calcular_stats_iniciais(view.raca, view.classe)
            database.create_player(ctx.author.id, view.nome, view.raca, view.classe, stats)
            
            final_embed = discord.Embed(
                title="📜 Personagem Criado com Sucesso! 📜",
                description=f"Bem-vindo(a) a Aethelgard, **{view.nome}**! Você é um(a) **{view.raca} {view.classe}** destinado(a) à grandeza.\n\nUse o comando `.perfil` para ver seus status. Sua jornada começa agora!",
                color=discord.Color.green()
            )
            await message.edit(embed=final_embed, view=None)
        else:
            await message.edit(content="A criação de personagem foi cancelada ou o tempo expirou.", embed=None, view=None)

    @commands.command(name="diario")
    async def diario(self, ctx):
        """Resgate sua recompensa diária de +30 Energia."""
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Você precisa criar um personagem primeiro! Use `.iniciar`.")
            return

        if player['last_daily']:
            last_daily_time = datetime.datetime.fromisoformat(player['last_daily'])
            cooldown = datetime.timedelta(hours=24)
            
            if datetime.datetime.now(datetime.timezone.utc) < last_daily_time + cooldown:
                tempo_restante = (last_daily_time + cooldown) - datetime.datetime.now(datetime.timezone.utc)
                horas, rem = divmod(tempo_restante.seconds, 3600)
                minutos, _ = divmod(rem, 60)
                await ctx.send(f"Você já resgatou sua recompensa diária! Tente novamente em **{horas}h e {minutos}m**.")
                return

        energia_ganha = 30
        nova_energia = database.update_player_energy(ctx.author.id, energia_ganha)
        database.update_last_daily(ctx.author.id)

        embed = discord.Embed(
            title="☀️ Recompensa Diária Resgatada! ☀️",
            description=f"Você descansou e recuperou suas forças, **{player['nome']}**!\n"
                        f"Você ganhou **+{energia_ganha} ⚡ Energia**.",
            color=discord.Color.yellow()
        )
        embed.set_footer(text=f"Sua energia agora é: {nova_energia}/{player['energia_max']}")
        await ctx.send(embed=embed)

    @commands.command(name="inventario", aliases=["inv"])
    async def inventario(self, ctx):
        """Mostra os itens no seu inventário."""
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Você precisa criar um personagem primeiro! Use `.iniciar`.")
            return

        inventory_items = database.get_player_inventory(ctx.author.id)
        if not inventory_items:
            await ctx.send("🎒 Seu inventário está vazio.")
            return
            
        embed = discord.Embed(title=f"🎒 Inventário de {player['nome']}", color=discord.Color.dark_green())
        
        # Agrupa itens por tipo para uma exibição organizada
        items_by_type = {}
        for item in inventory_items:
            tipo = item['tipo']
            if tipo not in items_by_type:
                items_by_type[tipo] = []
            items_by_type[tipo].append(f"x{item['quantity']} {item['nome']} ({item['raridade']})")

        for tipo, items in items_by_type.items():
            embed.add_field(name=f"**{tipo}**", value="\n".join(items), inline=False)
            
        await ctx.send(embed=embed)

    @commands.command(name="usar")
    async def usar_item(self, ctx, *, nome_item: str):
        """Usa um item consumível do seu inventário."""
        try:
            player = database.get_player(ctx.author.id)
            if not player:
                await ctx.send("Você precisa criar um personagem primeiro! Use `.iniciar`.")
                return

            inventory = database.get_player_inventory(ctx.author.id)
            item_to_use = next((item for item in inventory if item['nome'].strip().lower() == nome_item.strip().lower()), None)
            
            if not item_to_use:
                await ctx.send(f"Você não possui o item `{nome_item}` no seu inventário.")
                return

            if item_to_use['tipo'] not in ['Consumível', 'Poção', 'Comida', 'Óleo', 'Bomba', 'Armadilha']:
                await ctx.send(f"`{item_to_use['nome']}` não é um item que pode ser usado desta forma.")
                return
                
            if not database.remove_item_from_inventory(ctx.author.id, item_to_use['item_id'], 1):
                await ctx.send("Ocorreu um erro ao consumir o item do inventário.")
                return
            
            # --- NOVO MOTOR DE EFEITOS EXPANDIDO ---
            efeitos = json.loads(item_to_use['efeitos']) if item_to_use['efeitos'] else {}
            
            resposta_embed = discord.Embed(title=f"🧪 Item Usado: {item_to_use['nome']}", color=discord.Color.teal())
            efeitos_aplicados = []

            if 'on_use' in efeitos:
                # O efeito pode ser uma lista de dicionários ou um único dicionário
                on_use_effects = efeitos['on_use'] if isinstance(efeitos['on_use'], list) else [efeitos['on_use']]

                for efeito_dict in on_use_effects:
                    efeito = efeito_dict.get('effect')
                    
                    if efeito == 'heal':
                        amount = efeito_dict.get('amount')
                        if amount:
                            hp_antes = player['hp']
                            new_hp = database.update_player_hp(ctx.author.id, amount)
                            efeitos_aplicados.append(f"❤️ Recuperou **{new_hp - hp_antes} de HP**!")
                    
                    elif efeito == 'restore_mp':
                        amount = efeito_dict.get('amount')
                        if amount:
                            mp_antes = player['mp']
                            new_mp = database.update_player_mp(ctx.author.id, amount)
                            efeitos_aplicados.append(f"💧 Recuperou **{new_mp - mp_antes} de MP**!")

                    elif efeito == 'buff':
                        stat = efeito_dict.get('stat')
                        amount = efeito_dict.get('amount')
                        duration = efeito_dict.get('duration_minutes')
                        if all([stat, amount, duration]):
                            database.apply_buff(ctx.author.id, item_to_use['nome'], stat, amount, duration)
                            efeitos_aplicados.append(f"💪 Ganhou um bônus de **+{amount} em {stat.upper()}** por {duration} minutos!")
                    
                    elif efeito == 'cure':
                        status = efeito_dict.get('status', [])
                        status_list = status if isinstance(status, list) else [status]
                        efeitos_aplicados.append(f"✨ Você se sente purificado(a) de `{', '.join(status_list)}`!")

            if not efeitos_aplicados:
                resposta_embed.description = "Você usou o item, mas ele não pareceu ter um efeito imediato."
            else:
                resposta_embed.description = "\n".join(efeitos_aplicados)
                
            await ctx.send(embed=resposta_embed)

        except Exception as e:
            await ctx.send("🔴 Ocorreu um erro inesperado ao tentar usar este item. Verifique o console.")
            print(f"Erro no comando .usar: {e}")

    @commands.command(name="perfil")
    async def perfil(self, ctx):
        """Mostra o seu perfil de aventureiro com status totais."""
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Você ainda não criou um personagem! Use `.iniciar` para começar.")
            return

        total_stats = database.get_player_total_stats(ctx.author.id)
        equipment_names = database.get_player_equipment_names(ctx.author.id)
        
        embed = discord.Embed(color=discord.Color.random())
        
        titulo = player['titulo'] or "Aventureiro(a)"
        raca_emoji = RACAS_BONUS.get(player['raca'], {}).get('emoji', '')
        classe_emoji = CLASSES_BASE.get(player['classe'], {}).get('emoji', '')
        embed.set_author(name=f"{player['nome']} - [{titulo}]", icon_url=ctx.author.display_avatar.url)
        embed.title = f"Nível {player['nivel']} - {raca_emoji} {player['raca']} {classe_emoji} {player['classe']}"
        
        embed.add_field(
            name="Recursos Vitais",
            value=f"❤️ **HP:** {player['hp']} / {player['hp_max']}\n"
                  f"💧 **MP:** {player['mp']} / {player['mp_max']}\n"
                  f"⚡ **Energia:** {player['energia']} / {player['energia_max']}\n"
                  f"⚔️ **Ataque:** {total_stats['ataque_total']}\n"
                  f"🛡️ **Defesa:** {total_stats['defesa_total']}",
            inline=True
        )

        stats_display = ""
        for stat, base_value in [('forca', 'FOR'), ('destreza', 'DES'), ('inteligencia', 'INT'), ('constituicao', 'CON'), ('sorte', 'SOR')]:
            total_value = total_stats.get(stat, player[stat])
            bonus = total_value - player[stat]
            emoji = {'FOR':'💪', 'DES':'🤸', 'INT':'🧠', 'CON':'맷', 'SOR':'🍀'}[base_value]
            
            if bonus > 0:
                stats_display += f"{emoji} **{base_value}:** {total_value} ({player[stat]} `+{bonus}`)\n"
            else:
                stats_display += f"{emoji} **{base_value}:** {total_value}\n"
        embed.add_field(name="Atributos Totais", value=stats_display, inline=True)
        
        slots_para_exibir = [
            ('cabeca', '🛡️'), ('peitoral', '🎽'), ('calcas', '👖'),
            ('botas', '👢'), ('luvas', '🧤'), ('arma', '⚔️'), ('acessorio', '💍')
        ]
        
        equipment_display = []
        for slot, emoji in slots_para_exibir:
            item_name = equipment_names.get(slot) or 'Vazio'
            equipment_display.append(f"{emoji} **{slot.capitalize()}:** {item_name}")

        embed.add_field(
            name="Equipamento",
            value="\n".join(equipment_display),
            inline=False
        )

        embed.add_field(
            name="Progresso e Riqueza",
            value=f"💰 **Ouro:** {player['gold']} Moedas\n"
                  f"📈 **EXP:** {player['exp']} / {player['exp_para_upar']}",
            inline=False
        )
        
        embed.set_footer(text=f"Aventura iniciada em Aethelgard.")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name="equipar")
    async def equipar_item(self, ctx, *, nome_item: str):
        """Equipa um item do seu inventário."""
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Crie um personagem com `.iniciar` primeiro.")
            return

        inventory = database.get_player_inventory(ctx.author.id)
        item_to_equip = None
        for item in inventory:
            if item['nome'].strip().lower() == nome_item.strip().lower():
                item_to_equip = item
                break
        
        if not item_to_equip:
            await ctx.send(f"Você não possui o item `{nome_item}` no seu inventário.")
            return

        slot = item_to_equip['slot']
        
        if not slot or slot == 'nenhum':
            await ctx.send(f"`{item_to_equip['nome']}` não é um item equipável.")
            return

        if not database.remove_item_from_inventory(ctx.author.id, item_to_equip['item_id'], 1):
            await ctx.send("Ocorreu um erro ao tentar equipar o item.")
            return

        database.equip_item(ctx.author.id, item_to_equip)
        
        await ctx.send(f"✅ Item **{item_to_equip['nome'].strip()}** equipado no slot `{slot}`!")

    @equipar_item.error
    async def equipar_item_error(self, ctx, error):
        """Manipulador de erros para o comando .equipar."""
        print(f"\n!!! ERRO CAPTURADO PELO HANDLER no comando '.equipar': {error}\n")
        
        await ctx.send(f"🔴 **Ocorreu um erro crítico ao tentar equipar!**\n"
                       f"Por favor, mostre este erro para o desenvolvedor:\n"
                       f"```{error}```")
        
    @commands.command(name="desequipar")
    async def desequipar_item(self, ctx, slot: str):
        """Desequipa um item de um slot específico."""
        player = database.get_player(ctx.author.id)
        if not player:
            await ctx.send("Crie um personagem com `.iniciar` primeiro.")
            return
        
        valid_slots = list(set(SLOTS.values()))
        
        if slot.lower() not in valid_slots:
            await ctx.send(f"Slot inválido! Slots disponíveis: `{', '.join(valid_slots)}`")
            return

        item_name = database.unequip_item(ctx.author.id, slot.lower())

        if item_name:
            await ctx.send(f"↩️ Item **{item_name}** desequipado e devolvido ao inventário.")
        else:
            await ctx.send(f"Você não tem nenhum item equipado no slot `{slot}`.")
        
async def setup(bot):
    await bot.add_cog(RPGCommands(bot))