import os
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from core.commands.onlinefix.interface import OnlineFixCommandInterface
from core.modules.steam.index import SteamSearch

load_dotenv()

class OnlineFixCommand(OnlineFixCommandInterface):
    def __init__(self, bot: commands.Bot, base_url: str):
        self.bot = bot
        self.base_url = base_url
        self.steam_search = SteamSearch(base_url)

    async def search_files(self, search_term: str):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            data = response.json()

            matches = [
                download for download in data.get("downloads", [])
                if search_term.lower() in download["title"].lower()
            ]

            return matches
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API: {e}")
            return None

    async def handle_no_results(self, search_term: str, ctx):
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
        just_download_channel = discord.utils.get(ctx.guild.text_channels, name="just-download")

        if not just_download_channel:
            permissions = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            just_download_channel = await ctx.guild.create_text_channel('just-download', overwrites=permissions)
            await just_download_channel.send("Canal 'just-download' criado!")

        if matches:
            
            for match in matches:
                steam_matches = await self.steam_search.search_steam_games(match['title'])
                game_details = None
                
                if steam_matches:
                    game_details = await self.steam_search.get_steam_game_details(steam_matches[0]['appid'])

                embed = discord.Embed(
                    title="🎯 Resultado Encontrado",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Título", value=match['title'], inline=False)
                embed.add_field(name="Tamanho do Arquivo", value=match['fileSize'], inline=True)
                embed.add_field(name="Data de Upload", value=match['uploadDate'], inline=True)
                embed.add_field(
                    name="Magnet Link : ",
                    value={match['uris'][0]},
                    inline=False
                )

                if game_details:
                    embed.add_field(name="Jogo na Steam", value=game_details.get('name', 'Desconhecido'), inline=False)
                    embed.add_field(name="Descrição", value=game_details.get('short_description', 'Não disponível'), inline=False)
                    embed.add_field(name="Preço", value=game_details.get('price_overview', {}).get('final_formatted', 'Gratuito'), inline=True)

                embed.set_footer(text="Buscas realizadas com sucesso! 🎮")
                await just_download_channel.send(embed=embed)
                await just_download_channel.send("---------------------------------------------------")
        else:
            await just_download_channel.send("🔍 Nenhum arquivo encontrado.")

@commands.command()
async def onlinef(ctx, *, search_term: str):
    base_url = os.getenv("BASE_URL")
    if not base_url:
        await ctx.send("⚠️ URL da API não configurada. Verifique o arquivo .env.")
        return

    command = OnlineFixCommand(ctx.bot, base_url)

    matches = await command.search_files(search_term)

    if matches is None or not matches:
        await command.handle_no_results(search_term, ctx)
    else:
        await command.send_results(matches, ctx)
