# cogs/_rpg_combat_view.py
import discord
from discord import ui
import random
import json

from rpg import database
from rpg.game_data import HABILIDADES

# --- Classe para o Menu de Seleção de Habilidades (Corrigida) ---
class SkillSelect(ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = []
        
        known_skills = self.parent_view.known_skills
        # CORREÇÃO: Usando player_mp em vez de player_hp
        player_mp = self.parent_view.player_mp

        for skill_key in known_skills:
            skill_data = HABILIDADES.get(skill_key)
            if skill_data:
                if player_mp >= skill_data['custo_mp']:
                    label = f"{skill_data['nome']} ({skill_data['custo_mp']} MP)"
                    options.append(discord.SelectOption(label=label, value=skill_key, description=skill_data['descricao']))
                else:
                    label = f"{skill_data['nome']} ({skill_data['custo_mp']} MP)"
                    options.append(discord.SelectOption(label=label, value=f"disabled_{skill_key}", description="Você não tem mana suficiente.", emoji="❌"))

        if not options:
            # Se não houver skills, cria uma opção placeholder desabilitada
            options.append(discord.SelectOption(label="Nenhuma habilidade conhecida", value="placeholder", emoji="🚫"))
            placeholder = "Você não conhece nenhuma habilidade."
            disabled = True
        else:
            placeholder = "Escolha uma habilidade para usar..."
            disabled = False
            
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, disabled=disabled, row=1)
            

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            skill_key = self.values[0]
            if skill_key.startswith("disabled_"):
                await interaction.followup.send("Você não tem mana suficiente para usar esta habilidade!", ephemeral=True)
                # Recarrega a UI principal sem gastar o turno
                await self.parent_view.update_ui(interaction)
                return

            skill_data = HABILIDADES.get(skill_key)
            self.parent_view.player_mp = database.update_player_mp(interaction.user.id, -skill_data['custo_mp'])
            await self.parent_view.player_skill_turn(interaction, skill_data)
        except Exception as e:
            print(f"Erro no callback do SkillSelect: {e}")
            await interaction.followup.send("Ocorreu um erro ao usar a habilidade.", ephemeral=True)


# --- Classe para o Menu de Seleção de Itens ---
class ItemSelect(ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = []
        usables = ['Consumível', 'Poção', 'Comida']
        for item in self.parent_view.inventory:
            if item['tipo'] in usables:
                options.append(discord.SelectOption(label=f"{item['nome']} (x{item['quantity']})", value=str(item['item_id'])))
        if not options:
            options.append(discord.SelectOption(label="Nenhum item usável", value="placeholder", emoji="🚫"))
            placeholder = "Você não tem itens usáveis."
            disabled = True
        else:
            placeholder = "Escolha um item para usar..."
            disabled = False
            
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, disabled=disabled, row=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            selected_item_id = int(self.values[0])
            item_to_use = next((item for item in self.parent_view.inventory if item['item_id'] == selected_item_id), None)
            if item_to_use:
                self.parent_view.apply_item_effect(item_to_use)
                database.remove_item_from_inventory(interaction.user.id, selected_item_id, 1)
                await self.parent_view.monster_turn(interaction, defending=True)
        except Exception as e:
            print(f"Erro no callback do ItemSelect: {e}")
            await interaction.followup.send("Ocorreu um erro ao usar o item.", ephemeral=True)


# --- View Principal de Combate ---
class CombatView(ui.View):
    def __init__(self, combat_cog, author, player, monster):
        super().__init__(timeout=300)
        self.combat_cog = combat_cog
        self.author = author
        self.player_data = player
        self.monster_data = monster
        self.player_hp = player['hp']
        self.player_mp = player['mp']
        self.monster_hp = monster['hp_max']
        self.message = None
        self.log = [f"Um **{self.monster_data['nome']}** selvagem apareceu!"]
        self.inventory = []
        self.known_skills = database.get_player_skills(author.id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Esta batalha não é sua!", ephemeral=True)
            return False
        return True

    async def end_combat(self, embed):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(embed=embed, view=self)
        self.stop()

    async def update_ui(self, interaction: discord.Interaction):
        self.clear_items()
        self.add_item(self.ataque_basico)
        self.add_item(self.habilidades)
        self.add_item(self.usar_item)
        self.add_item(self.fugir)
        player_status_str = " ".join([f"⚫️ {s.capitalize()}({d['duracao']})" for s, d in self.player_statuses.items()])
        monster_status_str = " ".join([f"⚫️ {s.capitalize()}({d['duracao']})" for s, d in self.monster_statuses.items()])
        embed = discord.Embed(title=f"⚔️ Batalha: {self.player_data['nome']} vs. {self.monster_data['nome']}", color=discord.Color.red())
        embed.add_field(name="Sua Vida/Mana ❤️💧", value=f"**HP:** {self.player_hp}/{self.player_data['hp_max']}\n**MP:** {self.player_mp}/{self.player_data['mp_max']}\n{player_status_str}", inline=True)
        embed.add_field(name=f"Vida do Monstro 👹", value=f"**{self.monster_hp} / {self.monster_data['hp_max']}**\n{monster_status_str}", inline=True)
        embed.add_field(name="Registro de Combate", value="\n".join(self.log), inline=False)
        
        await interaction.message.edit(embed=embed, view=self)

    def _process_statuses(self, target_hp, statuses):
        """Processa efeitos de status como veneno e regeneração no início do turno."""
        damage_taken = 0
        log_updates = []
        
        # Itera sobre uma cópia para poder remover itens do dicionário original
        for status, data in list(statuses.items()):
            if status == 'veneno':
                damage = data['dano']
                target_hp -= damage
                log_updates.append(f"🩸 O veneno causa **{damage}** de dano!")
            
            data['duracao'] -= 1
            if data['duracao'] <= 0:
                log_updates.append(f"✨ O efeito **{status.capitalize()}** passou.")
                del statuses[status]
        
        return target_hp, log_updates

    def apply_item_effect(self, item):
        """Aplica os efeitos de um item consumível durante o combate."""
        efeitos = json.loads(item['efeitos']) if item['efeitos'] else {}
        self.log = [f"Você usou **{item['nome']}**."] # Reinicia o log do turno

        if 'on_use' in efeitos:
            on_use_effects = efeitos['on_use'] if isinstance(efeitos['on_use'], list) else [efeitos['on_use']]
            
            for efeito_dict in on_use_effects:
                efeito = efeito_dict.get('effect')
                if efeito == 'heal':
                    amount = efeito_dict.get('amount')
                    if amount:
                        hp_antes = self.player_hp
                        new_hp_db = database.update_player_hp(self.author.id, amount)
                        healed_amount = new_hp_db - hp_antes
                        self.player_hp = new_hp_db
                        self.log.append(f"❤️ Você recuperou **{healed_amount} de HP**!")
                
                elif efeito == 'restore_mp':
                    amount = efeito_dict.get('amount')
                    if amount:
                        mp_antes = self.player_mp
                        new_mp_db = database.update_player_mp(self.author.id, amount)
                        restored_amount = new_mp_db - mp_antes
                        self.player_mp = new_mp_db
                        self.log.append(f"💧 Você recuperou **{restored_amount} de MP**!")

    async def monster_turn(self, interaction: discord.Interaction, defending: bool = False):
        player_stats = database.get_player_total_stats(self.author.id)

        self.monster_hp, status_logs = self._process_statuses(self.monster_hp, self.monster_statuses)
        self.log.extend(status_logs)
        if self.monster_hp <= 0:
            await self.handle_victory()
            return
        
        # Fórmula de Defesa do Jogador
        poder_defesa_player = player_stats.get('constituicao', 0) + player_stats.get('defesa', 0)
        
        # Fórmula de Dano do Monstro com d20
        rolagem_monstro = random.randint(1, 20)
        dano_bruto_monstro = self.monster_data['ataque'] + rolagem_monstro
        reducao_dano = int(poder_defesa_player / 2)
        dano_final_monstro = max(1, dano_bruto_monstro - reducao_dano)
        
        log_rolagem = f"(Rolagem: {rolagem_monstro})"
        if rolagem_monstro == 1: log_rolagem = "(ERRO CRÍTICO!)"
        if rolagem_monstro == 20: log_rolagem = "(ACERTO CRÍTICO!)"

        if defending:
            dano_final_monstro = max(1, dano_final_monstro // 2)
            self.log.append(f"🛡️ Em postura defensiva, você amortece o golpe!")

        

        new_hp_db = database.update_player_hp(self.author.id, -dano_final_monstro)
        self.player_hp = new_hp_db
        self.log.append(f"O {self.monster_data['nome']} atacou {log_rolagem} e causou **{dano_final_monstro}** de dano a você!")


    async def player_skill_turn(self, interaction: discord.Interaction, skill_data):
        """Executa o turno completo do jogador ao usar uma habilidade, aplicando seus efeitos."""
        try:
            self.log = [f"Você usa **{skill_data['nome']}**!"]
            player_stats = database.get_player_total_stats(self.author.id)
            
            bonus_crit_chance = 0
            armor_penetration = 0
            
            # 1. Lê os efeitos da habilidade
            if 'efeitos' in skill_data and 'on_hit' in skill_data['efeitos']:
                efeito = skill_data['efeitos']['on_hit']
                if efeito.get('tipo') == 'bonus_crit_chance':
                    bonus_crit_chance = efeito.get('valor', 0)
                    self.log.append(f"🎯 Sua mira se foca, aumentando a chance de crítico!")
                
                if efeito.get('tipo') == 'armor_penetration_percent':
                    armor_penetration = efeito.get('valor', 0)
                    self.log.append(f"🔪 Seu golpe procura por uma brecha na armadura!")

            # 2. Calcula o dano base da habilidade
            scaling_stat_value = player_stats.get(skill_data['escala_atributo'], 0)
            dano_base_skill = int(skill_data.get('dano_base', 0) + (scaling_stat_value * skill_data.get('multiplicador', 0)))
            
            # 3. Calcula a chance de crítico e a rolagem do d20
            chance_de_critico_total = 5 + (player_stats.get('sorte', 0) / 10) + bonus_crit_chance # 5% de base + Sorte + Bônus da Skill
            rolagem_critico = random.randint(1, 100)
            is_crit = rolagem_critico <= chance_de_critico_total
            
            # 4. Calcula a defesa do monstro (considerando a penetração de armadura)
            defesa_efetiva_monstro = self.monster_data['defesa'] * (1 - armor_penetration)
            reducao_dano = int(defesa_efetiva_monstro / 2)
            
            # 5. Calcula o dano final
            dano_final_skill = max(1, dano_base_skill - reducao_dano)
            if is_crit:
                dano_final_skill = int(dano_final_skill * 1.5) # Dano crítico causa 50% a mais
                self.log.append("💥 **ACERTO CRÍTICO!**")

            self.monster_hp -= dano_final_skill
            self.log.append(f"Você causou **{dano_final_skill}** de dano com sua habilidade!")

            # 6. Continua o fluxo da batalha
            if self.monster_hp <= 0:
                await self.handle_victory()
                return
            
            await self.monster_turn(interaction)

            if self.player_hp <= 0:
                await self.handle_defeat()
                return
            
            await self.update_ui(interaction)
        except Exception as e:
            print(f"Erro na função player_skill_turn: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro ao processar a habilidade!", ephemeral=True)

    @ui.button(label="Ataque Básico ⚔️", style=discord.ButtonStyle.danger, row=0)
    async def ataque_basico(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        try:
            self.log = []
            # Processa status do jogador no início do turno (ex: veneno)
            self.player_hp, status_logs = self._process_statuses(self.player_hp, self.player_statuses)
            self.log.extend(status_logs)
            if self.player_hp <= 0:
                await self.handle_defeat()
                return

            player_stats = database.get_player_total_stats(self.author.id)
            
            # --- LÓGICA DE DANO COM D20 ---
            poder_ataque_player = max(player_stats['forca'], player_stats['destreza']) + player_stats.get('dano', 0)
            rolagem_player = random.randint(1, 20)
            is_crit = (rolagem_player == 20)
            dano_bruto_player = poder_ataque_player + rolagem_player
            reducao_dano = int(self.monster_data['defesa'] / 2)
            dano_final_player = max(1, dano_bruto_player - reducao_dano)
            
            log_rolagem = f"(Rolagem: {rolagem_player})"
            if is_crit: log_rolagem = "💥 (ACERTO CRÍTICO!)"
            if rolagem_player == 1: log_rolagem = "😩 (ERRO CRÍTICO!)"

            self.monster_hp -= dano_final_player
            self.log.append(f"Você atacou {log_rolagem} o {self.monster_data['nome']} e causou **{dano_final_player}** de dano!")
            
            # --- NOVO: VERIFICA EFEITOS DA ARMA ---
            weapon = database.get_equipped_weapon(self.author.id)
            if weapon and weapon['efeitos']:
                efeitos_arma = json.loads(weapon['efeitos'])
                
                # Verifica efeitos 'on_hit' (a cada ataque)
                if 'on_hit' in efeitos_arma and random.random() < efeitos_arma['on_hit'].get('chance', 1.0):
                    efeito = efeitos_arma['on_hit']
                    if efeito.get('tipo') == 'status':
                        self.monster_statuses[efeito['status']] = {"duracao": efeito['duracao'], "dano": efeito.get('dano', 0)}
                        self.log.append(f"🩸 Sua arma inflige **{efeito['status'].capitalize()}** no inimigo!")

                # Verifica efeitos 'on_crit' (apenas em acertos críticos)
                if is_crit and 'on_crit' in efeitos_arma and random.random() < efeitos_arma['on_crit'].get('chance', 1.0):
                    efeito = efeitos_arma['on_crit']
                    if efeito.get('tipo') == 'status':
                        self.monster_statuses[efeito['status']] = {"duracao": efeito['duracao'], "dano": efeito.get('dano', 0)}
                        self.log.append(f"💥 Seu acerto crítico inflige **{efeito['status'].capitalize()}** no inimigo!")

            # --- FIM DA VERIFICAÇÃO DE EFEITOS ---

            if self.monster_hp <= 0:
                await self.handle_victory()
                return
            
            await self.monster_turn(interaction)
            if self.player_hp <= 0:
                await self.handle_defeat()
                return
            await self.update_ui(interaction)
        except Exception as e:
            print(f"Erro no botão de ataque básico: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro inesperado durante o ataque! Verifique o console.", ephemeral=True)
            
    async def ataque_basico(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        try:
            self.log = []
            player_stats = database.get_player_total_stats(self.author.id)
            
            # Fórmula de Ataque do Jogador
            poder_ataque_player = max(player_stats['forca'], player_stats['destreza']) + player_stats.get('dano', 0)
            
            # Fórmula de Dano do Jogador com d20
            rolagem_player = random.randint(1, 20)
            dano_bruto_player = poder_ataque_player + rolagem_player
            reducao_dano = int(self.monster_data['defesa'] / 2)
            dano_final_player = max(1, dano_bruto_player - reducao_dano)
            
            log_rolagem = f"(Rolagem: {rolagem_player})"
            if rolagem_player == 1: log_rolagem = "(ERRO CRÍTICO!)"
            if rolagem_player == 20: log_rolagem = "(ACERTO CRÍTICO!)"

            self.monster_hp -= dano_final_player
            self.log.append(f"Você atacou {log_rolagem} o {self.monster_data['nome']} e causou **{dano_final_player}** de dano!")
            
            if self.monster_hp <= 0:
                await self.handle_victory()
                return
            
            await self.monster_turn(interaction)
            if self.player_hp <= 0:
                await self.handle_defeat()
                return
            await self.update_ui(interaction)
        except Exception as e:
            print(f"Erro no botão de ataque básico: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro inesperado durante o ataque! Verifique o console.", ephemeral=True)

    @ui.button(label="Habilidades ", style=discord.ButtonStyle.primary, row=0)
    async def habilidades(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        try:
            self.clear_items()
            self.add_item(self.ataque_basico)
            self.add_item(self.habilidades)
            self.add_item(self.usar_item)
            self.add_item(self.fugir)
            self.add_item(SkillSelect(self))
            await interaction.message.edit(view=self)
            await interaction.followup.send("Escolha uma habilidade para usar:", ephemeral=True)
        except Exception as e:
            print(f"Erro no botão de habilidades: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro ao tentar abrir as habilidades!", ephemeral=True)

    @ui.button(label="Usar Item 🎒", style=discord.ButtonStyle.success, row=0)
    async def usar_item(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        try:
            self.inventory = database.get_player_inventory(self.author.id)
            self.clear_items()
            self.add_item(self.ataque_basico)
            self.add_item(self.habilidades)
            self.add_item(self.usar_item)
            self.add_item(self.fugir)
            self.add_item(ItemSelect(self))
            await interaction.message.edit(view=self)
            await interaction.followup.send("Escolha um item do seu inventário abaixo:", ephemeral=True)
        except Exception as e:
            print(f"Erro no botão de item: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro ao tentar abrir o inventário!", ephemeral=True)

    @ui.button(label="Fugir 🏃", style=discord.ButtonStyle.secondary, row=0)
    async def fugir(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        try:
            self.log = []
            chance = 0.5 + (self.player_data['sorte'] / 100)
            if random.random() < chance:
                await self.end_combat(discord.Embed(title="🏃 Fuga!", description="Você conseguiu fugir em segurança!", color=discord.Color.dark_grey()))
            else:
                self.log.append("Você tentou fugir, mas falhou!")
                await self.monster_turn(interaction)
                if self.player_hp > 0:
                    await self.update_ui(interaction)
        except Exception as e:
            print(f"Erro no botão de fugir: {e}")
            await interaction.followup.send("🔴 Ocorreu um erro ao tentar fugir! Verifique o console.", ephemeral=True)

    async def handle_victory(self):
        leveled_up = database.grant_rewards(self.player_data['user_id'], self.monster_data['exp_recompensa'], self.monster_data['gold_recompensa'])
        possible_drops = database.get_monster_drops(self.monster_data['monster_id'])
        looted_items = []
        for drop in possible_drops:
            if random.uniform(0, 100) < drop['chance']:
                database.add_item_to_inventory(self.player_data['user_id'], drop['item_id'], 1)
                looted_items.append(drop['nome'])
        description = (f"Você derrotou o **{self.monster_data['nome']}**!\n\n"
                       f"**Recompensas:**\n"
                       f"💰 +{self.monster_data['gold_recompensa']} Ouro\n"
                       f"📈 +{self.monster_data['exp_recompensa']} EXP")
        if looted_items:
            description += "\n\n**Loot:**\n" + "\n".join([f"✅ {name}" for name in looted_items])
        embed = discord.Embed(title=f"🎉 VITÓRIA! 🎉", description=description, color=discord.Color.gold())
        if leveled_up:
            new_player_data = database.get_player(self.player_data['user_id'])
            embed.set_footer(text=f"Parabéns! Você avançou para o Nível {new_player_data['nivel']}!")
        await self.end_combat(embed)

    async def handle_defeat(self):
        embed = discord.Embed(title="💀 Você foi Derrotado!",
                              description=f"Você lutou bravamente, mas foi vencido pelo {self.monster_data['nome']}.\n"
                                          "Você não perdeu itens, mas precisa se recuperar.",
                              color=discord.Color.dark_red())
        await self.end_combat(embed)