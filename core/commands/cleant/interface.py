from abc import ABC, abstractmethod
from discord.ext import commands
import discord

class CleantCommandInterface(ABC):
    """
    Interface para o comando cleant.
    """

    @abstractmethod
    async def clean_channel(self, ctx: commands.Context):
        """
        Limpa todas as mensagens do canal.
        """
        pass

    @abstractmethod
    async def handle_permission_error(self, ctx: commands.Context):
        """
        Trata o erro de permissão ao tentar limpar o chat.
        """
        pass

    @abstractmethod
    async def handle_generic_error(self, ctx: commands.Context, error: Exception):
        """
        Trata erros genéricos ao executar o comando.
        """
        pass
