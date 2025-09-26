# cogs/rpg_system.py
from discord.ext import commands, tasks
from rpg import database

class RPGSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicia a tarefa de regeneração de energia assim que o Cog é carregado
        self.passive_energy_regen.start()

    def cog_unload(self):
        # Garante que a tarefa seja cancelada se o Cog for descarregado
        self.passive_energy_regen.cancel()

    @tasks.loop(minutes=30)
    async def passive_energy_regen(self):
        """A cada 30 minutos, regenera 1 de energia para todos os jogadores que precisam."""
        # Espera o bot estar totalmente pronto antes de cada execução do loop
        # Isso garante que a lista de jogadores seja pega apenas quando o bot estiver online e pronto
        await self.bot.wait_until_ready()
        
        players_to_regen = database.get_all_players_for_regen()
        if not players_to_regen:
            return
        
        print(f"[RPG System] Regenerando 1 de energia para {len(players_to_regen)} jogadores...")
        for player in players_to_regen:
            database.update_player_energy(player['user_id'], 1)
        print("[RPG System] Regeneração de energia concluída.")

    @passive_energy_regen.before_loop
    async def before_regen_loop(self):
        # Espera o bot estar totalmente pronto ANTES de iniciar o loop pela primeira vez
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(RPGSystem(bot))