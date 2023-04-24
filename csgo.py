import requests

def get_case_prices():
    response = requests.get("https://steamcommunity.com/market/search/render?norender=1&start=0&count=40&query=Case&category_730_Type[]=tag_CSGO_Type_WeaponCase")
    data = response.json()
    return {case.get("hash_name"): float(case.get("sell_price_text").replace("$","")) for case in data.get("results")}

def get_inventory(steamid):
    response = requests.get(f"https://steamcommunity.com/inventory/{steamid}/730/2")
    if response.status_code != 200:
        print(f"Error getting inventory: {response.status_code}")
        return None
    
    try:
        data = response.json()
        descriptions = {item.get("classid"): item.get("market_hash_name") for item in data.get("descriptions")}
        inventory = [descriptions[item.get("classid")] for item in data.get("assets")]
        return inventory
    except:
        print(f"Error getting inventory: {response.status_code}\n----------------\n{response.text}\n----------------")
        return None