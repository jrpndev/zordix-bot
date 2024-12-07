import requests
import os
from core.commands.top.interface import TopGamesCommandInterface
from discord.ext import commands
import discord

from dotenv import load_dotenv
load_dotenv()

class TopGamesCommand(TopGamesCommandInterface):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.base_url = os.getenv("BASE_URL")

    async def get_top_games(self, limit: int):
        """
        Realiza a requisição na API e retorna os jogos mais recentes, limitado pelo número fornecido.
        """
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  
            data = response.json()

            sorted_games = sorted(data.get("downloads", []), key=lambda x: x["uploadDate"], reverse=True)

            top_games = sorted_games[:limit]
            return top_games
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API: {e}")
            return None

    async def send_top_games(self, top_games, ctx):
        """
        Envia os jogos mais recentes para o canal 'just-download'. Caso o canal não exista, cria-o.
        """
        just_download_channel = discord.utils.get(ctx.guild.text_channels, name="just-download")
        
        if not just_download_channel:
            permissions = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            just_download_channel = await ctx.guild.create_text_channel('just-download', overwrites=permissions)
            await just_download_channel.send("Canal 'just-download' criado!")

        response_message = "🎮 Jogos mais recentes:\n"
        for game in top_games:
            response_message += (
                f"\n**Título:** {game['title']}\n"
                f"**Tamanho do Arquivo:** {game['fileSize']}\n"
                f"**Data de Upload:** {game['uploadDate']}\n"
                f"**Magnet Link:** {game['uris'][0]}\n"
            )

        await just_download_channel.send(response_message)

@commands.command()
async def top(ctx, number_of_games: int):
    """
    Comando para buscar os jogos mais recentes, com limite definido pelo usuário.
    """
    if number_of_games > 10:
        await ctx.send("⚠️ O número máximo de jogos que você pode solicitar é 10.")
        return

    command = TopGamesCommand(ctx.bot)
    
    top_games = await command.get_top_games(number_of_games)

    if top_games is None:
        await ctx.send("⚠️ Não foi possível acessar os jogos no momento. Tente novamente mais tarde.")
    else:
        await command.send_top_games(top_games, ctx)
