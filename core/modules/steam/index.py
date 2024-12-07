import os
import requests
from core.modules.steam.interface import SteamSearchInterface


class SteamSearch(SteamSearchInterface):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.steam_api_key = os.getenv("STEAM_API_KEY")
        self.steam_app_list_url = os.getenv("STEAM_APP_LIST_URL", "https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        self.steam_store_details_url = os.getenv("STEAM_STORE_DETAILS_URL", "https://store.steampowered.com/api/appdetails")

    async def search_steam_games(self, search_term: str):
        try:
            response = requests.get(self.steam_app_list_url)
            response.raise_for_status()
            app_list = response.json().get("applist", {}).get("apps", [])

            matches = [
                app for app in app_list if search_term.lower() in app["name"].lower()
            ][:5]

            return matches
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar a API da Steam: {e}")
            return None

    async def get_steam_game_details(self, app_id: int):
        try:
            response = requests.get(self.steam_store_details_url, params={"appids": app_id})
            response.raise_for_status()
            game_details = response.json().get(str(app_id), {}).get("data", {})
            return game_details
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar os detalhes do jogo: {e}")
            return None