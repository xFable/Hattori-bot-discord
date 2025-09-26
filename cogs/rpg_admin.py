import discord
from discord.ext import commands
import json
from collections import defaultdict

from rpg import database

# Dicionário para mapear raridades a cores para os embeds
RARITY_COLORS = {
    "⚪ Comum": discord.Color.light_grey(),
    "🟢 Incomum": discord.Color.green(),
    "🔵 Raro": discord.Color.blue(),
    "🟣 Épico": discord.Color.purple(),
    "🟠 Lendário": discord.Color.orange()
}

class RPGAdmin(commands.Cog):
    def __init__(self, bot):
        print(">>> Cog de Administração de RPG (rpg_admin.py) carregado com sucesso! <<<")
        self.bot = bot

    # Garante que todos os comandos neste Cog só podem ser usados por administradores
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command(name="additem")
    async def add_item(self, ctx, nome: str, tipo: str, slot: str, raridade: str, *bonus):
        bonus_stats = {}
        efeitos = {}

        for b in bonus:
            if b.lower().startswith("efeito:"):
                # Formato: efeito:tipo,subtipo,valor1,valor2...
                # Ex: efeito:on_hit,poison,0.25
                parts = b[7:].split(',')
                effect_type = parts[0]
                effect_details = parts[1:]
                if effect_type not in efeitos:
                    efeitos[effect_type] = []
                efeitos[effect_type].append(effect_details)
            else:
                try:
                    stat, value = b.split(':')
                    bonus_stats[stat.lower()] = int(value)
                except ValueError:
                    await ctx.send(f"⚠️ Formato de bônus inválido: `{b}`. Use `stat:valor` (ex: `for:5`).")
                    return
        
        try:
            database.add_item(
                nome=nome, tipo=tipo, slot=slot.lower(), raridade=raridade,
                bonus_stats=json.dumps(bonus_stats) if bonus_stats else None,
                efeitos=json.dumps(efeitos) if efeitos else None
            )
            await ctx.send(f"✅ Item **{nome}** criado com sucesso!")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao criar o item: {e}")

    @commands.command(name="iteminfo")
    async def item_info(self, ctx, *, nome_item: str):
        """Mostra informações detalhadas sobre um item."""
        item = database.get_item_by_name(nome_item)
        if not item:
            await ctx.send(f"🔎 Item `{nome_item}` não encontrado.")
            return

        cor = RARITY_COLORS.get(item['raridade'], discord.Color.default())
        embed = discord.Embed(title=f"{item['raridade']} {item['nome']}", color=cor)
        embed.add_field(name="Tipo/Slot", value=f"{item['tipo']} / {item['slot'] or 'Nenhum'}", inline=True)
        
        if item['bonus_stats']:
            stats = json.loads(item['bonus_stats'])
            stats_str = "\n".join([f"**{key.upper()}:** +{value}" for key, value in stats.items()])
            embed.add_field(name="Bônus de Atributos", value=stats_str, inline=True)
        
        # --- LÓGICA DE EXIBIÇÃO DE EFEITOS CORRIGIDA ---
        if item['efeitos']:
            effects = json.loads(item['efeitos'])
            effects_str = ""
            # Itera sobre cada tipo de efeito (especial, requisitos, etc.)
            for effect_type, effect_data in effects.items():
                # Formata o título do efeito
                effects_str += f"**{effect_type.replace('_', ' ').title()}:** "
                # Se o dado for uma lista, junta os itens. Se for texto, usa o texto.
                if isinstance(effect_data, list):
                    effects_str += ", ".join(map(str, effect_data))
                else:
                    effects_str += str(effect_data)
                effects_str += "\n"

            if effects_str:
                embed.add_field(name="Peculiaridades", value=effects_str, inline=False)
            
        embed.set_footer(text=f"ID do Item: {item['item_id']}")
        await ctx.send(embed=embed)

    @commands.command(name="delitem")
    async def delete_item(self, ctx, *, nome_item: str):
        """Apaga um item permanentemente do jogo."""
        item = database.get_item_by_name(nome_item)
        if not item:
            await ctx.send(f"🔎 Item `{nome_item}` não encontrado.")
            return

        # Sistema de confirmação para evitar acidentes
        view = discord.ui.View(timeout=30)
        confirm_button = discord.ui.Button(label="Sim, apagar!", style=discord.ButtonStyle.danger)
        cancel_button = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.secondary)

        async def confirm_callback(interaction: discord.Interaction):
            database.delete_item_by_name(nome_item)
            await interaction.response.edit_message(content=f"🗑️ Item **{nome_item}** foi apagado com sucesso.", view=None)
        
        async def cancel_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Operação cancelada.", view=None)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await ctx.send(f"**Tem certeza que deseja apagar o item `{nome_item}`?** Esta ação não pode ser desfeita.", view=view)


    @commands.command(name="listallitems")
    async def list_all_items(self, ctx):
        """Lista todos os itens do jogo, organizados por categoria com paginação."""
        
        todos_os_itens = database.get_all_items_for_listing()

        if not todos_os_itens:
            await ctx.send("❌ Nenhum item encontrado no banco de dados.")
            return

        items_por_tipo = defaultdict(list)
        for item in todos_os_itens:
            items_por_tipo[item['tipo']].append(f"{item['nome']} ({item['raridade']})")

        # --- LÓGICA DE PAGINAÇÃO ---
        
        embeds = []
        # Começamos com o primeiro embed
        current_embed = discord.Embed(
            title=f"📚 Catálogo de Itens de Aethelgard (Página 1)",
            description=f"Encontrados **{len(todos_os_itens)}** itens no total.",
            color=discord.Color.blue()
        )
        
        field_count = 0
        page_count = 1

        for tipo, lista_de_nomes in items_por_tipo.items():
            # Se adicionar este campo for exceder o limite, envie o embed atual e crie um novo
            if field_count >= 25:
                embeds.append(current_embed)
                page_count += 1
                current_embed = discord.Embed(
                    title=f"📚 Catálogo de Itens de Aethelgard (Página {page_count})",
                    color=discord.Color.blue()
                )
                field_count = 0

            valor_campo = "\n".join(lista_de_nomes)
            if len(valor_campo) > 1024:
                valor_campo = valor_campo[:1020] + "\n..."

            current_embed.add_field(name=f"**{tipo}**", value=valor_campo, inline=False)
            field_count += 1
        
        # Adiciona o último embed à lista
        embeds.append(current_embed)

        # Envia todos os embeds criados, um por um
        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.command(name="giveitem")
    async def give_item(self, ctx, member: discord.Member, quantity: int, *, nome_item: str):
        """Dá um item a um jogador. (Admin)"""
        player = database.get_player(member.id)
        if not player:
            await ctx.send(f"❌ O jogador {member.name} não encontrou um personagem.")
            return

        item = database.get_item_by_name(nome_item)
        if not item:
            await ctx.send(f"🔎 Item `{nome_item}` não encontrado no banco de dados.")
            return
        
        database.add_item_to_inventory(member.id, item['item_id'], quantity)
        await ctx.send(f"✅ Adicionado **{quantity}x {item['nome']}** ao inventário de {member.mention}.")
    
    @give_item.error
    async def give_item_error(self, ctx, error):
        """Manipulador de erros para o comando giveitem."""
        # Transforma o erro em uma forma mais legível
        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"🤔 Faltam argumentos! Você precisa me dizer para quem, quantos e qual item dar.\n"
                           f"**Uso correto:** `.giveitem @usuário <quantidade> \"<nome do item>\"`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ Não consegui encontrar o membro `{error.argument}`. "
                           f"Por favor, mencione um membro válido do servidor.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"🤔 A quantidade precisa ser um número inteiro!\n"
                           f"**Uso correto:** `.giveitem @usuário 5 \"Poção de Cura Fraca\"`")
        else:
            await ctx.send("Ocorreu um erro inesperado ao executar este comando.")
            print(f"Erro no comando 'give_item': {error}")

    @commands.command(name="sethp")
    async def set_hp(self, ctx, member: discord.Member, hp: int):
        """Define o HP atual de um jogador para testes."""
        database.update_player_hp(member.id, hp - database.get_player(member.id)['hp'])
        await ctx.send(f"HP de {member.mention} definido para {hp}.")

    @commands.command(name="addexp")
    async def add_exp(self, ctx, member: discord.Member, quantidade: int):
        """Adiciona EXP a um jogador e verifica se ele subiu de nível. (Admin)"""
        player = database.get_player(member.id)
        if not player:
            await ctx.send(f"❌ O jogador {member.name} não encontrou um personagem.")
            return

        leveled_up = database.grant_rewards(member.id, quantidade, 0) # Adiciona apenas EXP
        
        if leveled_up:
            new_player_data = database.get_player(member.id)
            await ctx.send(f"✅ Adicionado **{quantidade} EXP** para {member.mention}. Ele subiu para o **Nível {new_player_data['nivel']}**!")
        else:
            await ctx.send(f"✅ Adicionado **{quantidade} EXP** para {member.mention}.")

async def setup(bot):
    await bot.add_cog(RPGAdmin(bot))