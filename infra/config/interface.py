from abc import ABC, abstractmethod
import discord

class ConfigInterface(ABC):
    """
    Interface para configurações do bot, como a criação de canais e configuração de permissões.
    """

    @abstractmethod
    async def create_channel(self, guild: discord.Guild, channel_name: str, permissions: dict) -> discord.TextChannel:
        """
        Cria um canal no servidor com as permissões definidas.
        
        :param guild: O servidor onde o canal será criado.
        :param channel_name: O nome do canal a ser criado.
        :param permissions: Dicionário de permissões para o canal.
        :return: Canal criado.
        """
        pass

    @abstractmethod
    async def check_channel_exists(self, guild: discord.Guild, channel_name: str) -> discord.TextChannel:
        """
        Verifica se um canal com o nome fornecido já existe no servidor.
        
        :param guild: O servidor onde o canal será verificado.
        :param channel_name: O nome do canal a ser verificado.
        :return: Canal encontrado ou None.
        """
        pass
