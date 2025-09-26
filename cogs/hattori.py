import discord
from discord.ext import commands
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configura a API do Gemini com a nossa chave
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")
    print("Verifique se a GEMINI_API_KEY está correta no arquivo config.py")

class Hattori(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    @commands.command(name="hattori")
    async def hattori(self, ctx):
        """Inicia uma conversa privada com a IA Hattori."""
        thread_name = f"Conversa com Hattori - {ctx.author.name}"
        # O tipo 'private_thread' só pode ser visto pelo usuário e por quem tiver permissão
        try:
            thread = await ctx.channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread)
        except discord.Forbidden:
            # Se o bot não tiver permissão para criar tópicos, cria um tópico público
            thread = await ctx.channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)

        # 2. Inicia o histórico da conversa para este tópico
        self.conversations[thread.id] = self.model.start_chat(history=[
            {'role': 'user', 'parts': ['A partir de agora, você é Hattori, uma IA assistente amigável e prestativa dentro de um bot de Discord. Seja conciso em suas respostas. Apresente-se ao usuário.']},
            {'role': 'model', 'parts': ['Olá! Eu sou Hattori. Como posso ajudar você hoje?']}
        ])

        # 3. Envia a primeira mensagem no tópico
        await thread.send(f"Olá {ctx.author.mention}! Eu sou Hattori. Pode me perguntar qualquer coisa aqui neste tópico. Quando terminar, pode arquivá-lo.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignora mensagens de bots (incluindo as do próprio bot)
        if message.author.bot:
            return

        # Verifica se a mensagem está em um tópico que tem uma conversa ativa
        if message.channel.id in self.conversations:
            thread = message.channel
            
            # Avisa que a IA está "digitando..."
            async with thread.typing():
                try:
                    # Pega o histórico da conversa
                    chat_session = self.conversations[thread.id]
                    
                    # Envia a mensagem do usuário para a API do Gemini
                    response = await chat_session.send_message_async(message.content)
                    
                    # Envia a resposta da IA de volta para o tópico
                    await thread.send(response.text)
                    
                except Exception as e:
                    await thread.send("Desculpe, ocorreu um erro ao tentar me comunicar com meu cérebro. Tente novamente mais tarde.")
                    print(f"Erro na API do Gemini: {e}")
            
async def setup(bot):
    await bot.add_cog(Hattori(bot))