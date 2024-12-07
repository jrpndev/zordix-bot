import requests
import os
from core.commands.onlinefix.interface import OnlineFixCommandInterface
from discord.ext import commands
import discord

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

class OnlineFixCommand(OnlineFixCommandInterface):
    def __init__(self, bot: commands.Bot, base_url: str):
        self.bot = bot
        self.base_url = base_url

    async def search_files(self, search_term: str):
        """
        Realiza a requisição na API e filtra os arquivos conforme o termo de busca.
        Agora, busca qualquer resultado que contenha o termo.
        """
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            data = response.json()

            matches = [
                download for download in data.get("downloads", [])
                if search_term.lower() in download["title"].lower()
            ]
            
            return matches[:1]
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API: {e}")
            return None

    async def handle_no_results(self, search_term: str, ctx):
        """
        Envia uma mensagem quando nenhum arquivo for encontrado.
        Se o canal não existir, cria-o.
        """
        just_download_channel = discord.utils.get(ctx.guild.text_channels, name="just-download")
        if not just_download_channel:
            permissions = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            just_download_channel = await ctx.guild.create_text_channel('just-download', overwrites=permissions)
            await just_download_channel.send("Canal 'just-download' criado!")
        
        await just_download_channel.send(f"🔍 Nenhum arquivo encontrado para: `{search_term}`.")

    async def send_results(self, matches, ctx):
        """
        Envia o resultado encontrado para o canal "just-download". Se o canal não existir, cria-o.
        """
        just_download_channel = discord.utils.get(ctx.guild.text_channels, name="just-download")
        
        if not just_download_channel:
            permissions = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            just_download_channel = await ctx.guild.create_text_channel('just-download', overwrites=permissions)
            await just_download_channel.send("Canal 'just-download' criado!")

        if matches:
            match = matches[0]
            response_message = (
                f"🎯 **Resultado encontrado**:\n\n"
                f"**Título:** {match['title']}\n"
                f"**Tamanho do Arquivo:** {match['fileSize']}\n"
                f"**Data de Upload:** {match['uploadDate']}\n"
                f"**Magnet Link:** [Clique aqui para baixar]({match['uris'][0]})\n"
            )
            await just_download_channel.send(response_message)
        else:
            await just_download_channel.send("🔍 Nenhum arquivo encontrado.")

@commands.command()
async def online_fix(ctx, *, search_term: str):
    """
    Comando para buscar um arquivo específico na API e enviar os resultados.
    """
    base_url = os.getenv("BASE_URL")
    if not base_url:
        await ctx.send("⚠️ URL da API não configurada. Verifique o arquivo .env.")
        return
    
    command = OnlineFixCommand(ctx.bot, base_url)
    
    matches = await command.search_files(search_term)

    if matches is None:
        await command.handle_no_results(search_term, ctx)
    elif matches:
        await command.send_results(matches, ctx)
