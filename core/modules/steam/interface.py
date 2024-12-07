from abc import ABC, abstractmethod
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class SteamSearchInterface(ABC):
    @abstractmethod
    async def search_steam_games(self, search_term: str):
        pass

    @abstractmethod
    async def get_steam_game_details(self, app_id: int):
        pass

class SteamSearch(SteamSearchInterface):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.steam_api_key = os.getenv("STEAM_API_KEY")
        self.steam_app_list_url = os.getenv("STEAM_APP_LIST_URL", "https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        self.steam_store_details_url = os.getenv("STEAM_STORE_DETAILS_URL", "https://store.steampowered.com/api/appdetails")