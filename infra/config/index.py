# infra/config/config.py

import discord
from discord.ext import commands
from discord import Permissions
from .interface import ConfigInterface

class Config(ConfigInterface):
    async def create_channel(self, guild: discord.Guild, channel_name: str, permissions: dict) -> discord.TextChannel:
        """
        Cria o canal com o nome e permissões fornecidos.
        """
        channel = await self.check_channel_exists(guild, channel_name)
        if not channel:
            channel = await guild.create_text_channel(
                channel_name,
                overwrites=permissions
            )
            print(f"Canal '{channel_name}' criado com sucesso!")
        else:
            print(f"O canal '{channel_name}' já existe.")
        return channel

    async def check_channel_exists(self, guild: discord.Guild, channel_name: str) -> discord.TextChannel:
        """
        Verifica se o canal existe no servidor.
        """
        return discord.utils.get(guild.text_channels, name=channel_name)

