import discord
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Ativar a intenção de conteúdo das mensagens

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')

@bot.command(name="online_fix")
async def online_fix(ctx, *, search_term: str):
    """
    Comando para buscar um arquivo específico na API.
    Argumentos:
    - search_term: Nome ou parte do nome do arquivo a ser buscado.
    """
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Verifica erros na requisição
        data = response.json()
        
        # Filtrar arquivos pelo termo de busca
        matches = [
            download for download in data.get("downloads", [])
            if search_term.lower() in download["title"].lower()
        ]

        if not matches:
            await ctx.send(f"🔍 Nenhum arquivo encontrado para: `{search_term}`.")
            return

        # Enviar links magnéticos dos resultados encontrados
        response_message = f"🎯 Resultados encontrados para: `{search_term}`\n"
        for match in matches:
            response_message += (
                f"\n**Título:** {match['title']}\n"
                f"**Tamanho do Arquivo:** {match['fileSize']}\n"
                f"**Data de Upload:** {match['uploadDate']}\n"
                f"**Magnet Link:** {match['uris'][0]}\n"
            )
        
        await ctx.send(response_message)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar a API: {e}")
        await ctx.send("⚠️ Não foi possível acessar a API no momento. Tente novamente mais tarde.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        await ctx.send("⚠️ Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.")

# Iniciar o bot
bot.run(TOKEN)
