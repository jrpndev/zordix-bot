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
        self.steam_app_list_url = os.getenv("STEAM_APP_LIST_URL", "https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        self.steam_store_details_url = os.getenv("STEAM_STORE_DETAILS_URL", "https://store.steampowered.com/api/appdetails")

    async def search_files(self, search_term: str):
        """
        Realiza a requisição na API principal e filtra os arquivos pelo termo de busca.
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

    async def search_steam_games(self, search_term: str):
        """
        Busca uma lista de até 5 jogos correspondentes na Steam usando o nome.
        """
        try:
            # Busca a lista de aplicativos da Steam
            response = requests.get(self.steam_app_list_url)
            response.raise_for_status()
            app_list = response.json().get("applist", {}).get("apps", [])

            # Filtra jogos pelo termo de busca
            matches = [
                app for app in app_list if search_term.lower() in app["name"].lower()
            ][:5]  # Limita a 5 resultados

            return matches
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API da Steam: {e}")
            return None

    async def get_steam_game_details(self, app_id: int):
        """
        Busca os detalhes de um jogo específico na Steam pelo App ID.
        """
        try:
            response = requests.get(self.steam_store_details_url, params={"appids": app_id})
            response.raise_for_status()
            game_details = response.json().get(str(app_id), {}).get("data", {})
            return game_details
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar os detalhes do jogo: {e}")
            return None

    async def send_results(self, matches, ctx):
        """
        Envia os resultados da busca na API principal ao canal 'just-download'.
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

    async def send_steam_game_selection(self, matches, ctx):
        """
        Envia uma lista de jogos encontrados e aguarda o usuário escolher um.
        """
        if not matches:
            await ctx.send("❌ Nenhum jogo correspondente encontrado na Steam.")
            return

        # Cria uma mensagem com a lista de opções
        options = "\n".join(
            [f"{i + 1}. {game['name']} (App ID: {game['appid']})" for i, game in enumerate(matches)]
        )
        selection_message = await ctx.send(f"🎮 **Jogos encontrados:**\n\n{options}\n\nDigite o número para escolher um jogo ou aguarde 30 segundos para cancelar.")

        # Define um check para capturar apenas mensagens do autor no mesmo canal
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit()

        try:
            # Aguarda a resposta do usuário
            response = await ctx.bot.wait_for("message", check=check, timeout=30)
            selected_index = int(response.content) - 1

            if 0 <= selected_index < len(matches):
                # Busca os detalhes do jogo escolhido
                selected_game = matches[selected_index]
                game_details = await self.get_steam_game_details(selected_game["appid"])
                await self.send_steam_results(game_details, ctx)
            else:
                await ctx.send("❌ Seleção inválida.")
        except TimeoutError:
            await ctx.send("⏳ Tempo esgotado. Nenhuma seleção feita.")

    async def send_steam_results(self, game_details, ctx):
        """
        Envia os detalhes de um jogo específico da Steam.
        """
        if not game_details:
            await ctx.send("❌ Detalhes do jogo não encontrados.")
            return

        nome = game_details.get("name", "Desconhecido")
        descricao = game_details.get("short_description", "Sem descrição disponível.")
        preco_info = game_details.get("price_overview", {})
        preco = preco_info.get("final_formatted", "Gratuito") if preco_info else "Gratuito"
        app_id = game_details.get("steam_appid")
        url = f"https://store.steampowered.com/app/{app_id}"

        embed = discord.Embed(title=nome, url=url, description=descricao, color=discord.Color.blue())
        embed.add_field(name="Preço", value=preco, inline=True)
        embed.add_field(name="ID do Jogo", value=str(app_id), inline=True)
        embed.set_footer(text="Informações da Steam")
        await ctx.send(embed=embed)

# Comando do bot
@commands.command()
async def online_fix(ctx, *, search_term: str):
    """
    Comando para buscar um arquivo específico na API ou informações na Steam.
    """
    base_url = os.getenv("BASE_URL")
    if not base_url:
        await ctx.send("⚠️ URL da API não configurada. Verifique o arquivo .env.")
        return

    command = OnlineFixCommand(ctx.bot, base_url)

    # Busca arquivos na API principal
    matches = await command.search_files(search_term)
    if matches:
        await command.send_results(matches, ctx)

    # Busca informações do jogo na Steam
    await ctx.send("🔍 Arquivo não encontrado. Buscando jogos na Steam...")
    steam_matches = await command.search_steam_games(search_term)
    await command.send_steam_game_selection(steam_matches, ctx)
