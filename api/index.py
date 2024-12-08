import discord
import os
from discord.ext import commands
from core.commands.onlinefix.index import onlinef
from core.commands.top.index import top
from core.commands.cleant.index import cleant
from dotenv import load_dotenv
from infra.config.index import Config
from flask import Flask
import threading

load_dotenv()

# Flask setup for Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

# Discord bot setup
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

bot.add_command(onlinef) 
bot.add_command(top)
bot.add_command(cleant)

@bot.event
async def on_guild_join(guild: discord.Guild):
    """
    Cria automaticamente o canal 'just-download' quando o bot entra em um servidor.
    """
    print(f"O bot entrou no servidor: {guild.name}")
    
    config = Config()
    
    permissions = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    await config.create_channel(guild, "just-download", permissions)

# Start Flask in a separate thread
threading.Thread(target=run_flask).start()

# Run Discord bot
bot.run(TOKEN)
