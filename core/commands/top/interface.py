# commands/top/interface.py

from abc import ABC, abstractmethod

class TopGamesCommandInterface(ABC):
    """
    Interface para o comando top.
    """

    @abstractmethod
    async def get_top_games(self, limit: int):
        """
        Método que retorna os jogos mais recentes até o limite solicitado.
        """
        pass

    @abstractmethod
    async def send_top_games(self, top_games):
        """
        Método que envia os jogos mais recentes para o canal.
        """
        pass
