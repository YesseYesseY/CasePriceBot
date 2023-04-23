import requests
import json

class SteamManager:
    def get_case_prices(self):
        response = requests.get("https://steamcommunity.com/market/search/render?norender=1&start=0&count=40&query=Case&category_730_Type[]=tag_CSGO_Type_WeaponCase")
        data = response.json()
        return {case.get("hash_name"): float(case.get("sell_price_text").replace("$","")) for case in data.get("results")}
    
    def get_inventory(self, steamid):
        response = requests.get(f"https://steamcommunity.com/inventory/{steamid}/730/2")
        data = response.json()
        try:
            descriptions = {item.get("classid"): item.get("market_hash_name") for item in data.get("descriptions")}
        except:
            print(f"Error getting inventory: {response.status_code}")
            return []
        inventory = [descriptions[item.get("classid")] for item in data.get("assets")]
        return inventory