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
        self.steam_api_key = os.getenv("STEAM_API_KEY")
        self.steam_app_list_url = os.getenv("STEAM_APP_LIST_URL")
        self.steam_store_details_url = os.getenv("STEAM_STORE_DETAILS_URL")

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

    async def search_steam_game(self, search_term: str):
        """
        Busca informações de um jogo na Steam usando o nome.
        """
        try:
            # Busca a lista de aplicativos da Steam
            response = requests.get(self.steam_app_list_url)
            response.raise_for_status()
            app_list = response.json().get("applist", {}).get("apps", [])

            # Busca pelo jogo na lista de apps
            app_info = next((app for app in app_list if search_term.lower() in app["name"].lower()), None)
            if not app_info:
                return None

            app_id = app_info["appid"]

            # Busca detalhes do jogo
            details_response = requests.get(self.steam_store_details_url, params={"appids": app_id})
            details_response.raise_for_status()
            game_details = details_response.json().get(str(app_id), {}).get("data", {})

            return game_details
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API da Steam: {e}")
            return None

    async def send_steam_results(self, game_details, ctx):
        """
        Envia os resultados da busca por jogos na Steam ao canal "just-download".
        """
        just_download_channel = discord.utils.get(ctx.guild.text_channels, name="just-download")

        if not just_download_channel:
            permissions = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            just_download_channel = await ctx.guild.create_text_channel('just-download', overwrites=permissions)
            await just_download_channel.send("Canal 'just-download' criado!")

        if game_details:
            nome = game_details.get("name", "Desconhecido")
            descricao = game_details.get("short_description", "Sem descrição disponível.")
            preco = game_details.get("price_overview", {}).get("final_formatted", "Gratuito")
            app_id = game_details.get("steam_appid")
            url = f"https://store.steampowered.com/app/{app_id}"

            embed = discord.Embed(title=nome, url=url, description=descricao, color=discord.Color.blue())
            embed.add_field(name="Preço", value=preco, inline=True)
            embed.add_field(name="ID do Jogo", value=str(app_id), inline=True)
            embed.set_footer(text="Informações da Steam")
            await just_download_channel.send(embed=embed)
        else:
            await just_download_channel.send("❌ Jogo não encontrado na Steam.")

@commands.command()
async def online_fix(ctx, *, search_term: str):
    """
    Comando para buscar arquivos ou informações de jogos na Steam.
    """
    base_url = os.getenv("BASE_URL")
    if not base_url:
        await ctx.send("⚠️ URL da API não configurada. Verifique o arquivo .env.")
        return

    command = OnlineFixCommand(ctx.bot, base_url)

    # Tenta buscar na API principal primeiro
    matches = await command.search_files(search_term)

    if matches:
        await command.send_results(matches, ctx)
    else:
        # Se não encontrar, busca na Steam
        await ctx.send("🔍 Buscando informações do jogo na Steam...")
        game_details = await command.search_steam_game(search_term)

        if game_details:
            await command.send_steam_results(game_details, ctx)
        else:
            await command.handle_no_results(search_term, ctx)
