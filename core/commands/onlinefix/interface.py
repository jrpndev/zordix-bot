# commands/online-fix/interface.py

from abc import ABC, abstractmethod

class OnlineFixCommandInterface(ABC):
    """
    Interface para o comando online_fix.
    """

    @abstractmethod
    async def search_files(self, search_term: str):
        """
        Método que realiza a busca de arquivos na API.
        Deve retornar uma lista de arquivos encontrados.
        """
        pass

    @abstractmethod
    async def handle_no_results(self, search_term: str):
        """
        Método que lida com o caso quando nenhum arquivo for encontrado.
        """
        pass

    @abstractmethod
    async def send_results(self, matches):
        """
        Método que envia os resultados encontrados para o canal.
        """
        pass
