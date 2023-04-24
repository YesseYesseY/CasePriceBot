import os
import json
import time


print ("Converting old data to new data...")
# for each file in inventory_backups create a folder with the steamid in data/userdata and move the file into it and rename it to inventory.json
for file in os.listdir("inventory_backups"):
    if file.endswith(".json"):
        steamid = file.replace(".json", "")
        if not os.path.exists(f"data/userdata/{steamid}"):
            os.makedirs(f"data/userdata/{steamid}")
        with open(f"inventory_backups/{file}", "r") as f:
            inventory = json.load(f)
        with open(f"data/userdata/{steamid}/inventory.json", "w") as f:
            json.dump(inventory, f, indent=4)


# for each json file in inventory_info create a folder with the steamid in data/userdata and read the file and write it to inventory_stats.json
for file in os.listdir("inventory_info"):
    if file.endswith(".json"):
        steamid = file.replace(".json", "")
        if not os.path.exists(f"data/userdata/{steamid}"):
            os.makedirs(f"data/userdata/{steamid}")
        with open(f"inventory_info/{file}", "r") as f:
            inventory_info = json.load(f)
        with open(f"data/userdata/{steamid}/inventory_stats.json", "w") as f:
            json.dump({
                "HighestTotalPrice": round(inventory_info.get("highest_value"), 2),
                "LowestTotalPrice": round(inventory_info.get("lowest_value"), 2),
                "HighestTotalPriceDate": "Unknown",
                "LowestTotalPriceDate": "Unknown",
            }, f, indent=4)

# for each folder in inventory_info/{steamid}
for folder in os.listdir("inventory_info"):
    if os.path.isdir(f"inventory_info/{folder}"):
        # for each json file in folder
        for file in os.listdir(f"inventory_info/{folder}"):
            print(file)
            if file.endswith(".json"):
                with open(f"inventory_info/{folder}/{file}", "r") as f:
                    item_info = json.load(f)
                if not os.path.exists(f"data/userdata/{folder}/items"):
                    os.makedirs(f"data/userdata/{folder}/items")
                with open(f"data/userdata/{folder}/inventory.json", "r") as f:
                    inventory = json.load(f)
                with open(f"data/userdata/{folder}/items/{file}", "w") as f:                    
                    json.dump({
                        "HighestPrice": round(item_info.get("highest_value") / inventory.count(file.replace(".json", "")), 2),
                        "LowestPrice": round(item_info.get("lowest_value") / inventory.count(file.replace(".json", "")), 2),
                        "HighestPriceDate": "Unknown",
                        "LowestPriceDate": "Unknown",
                    }, f, indent=4)

# read chats_to_update.json 
with open("chats_to_update.json", "r") as f:
    chats_to_update = json.load(f)

for chat in chats_to_update:
    if not os.path.exists(f"data/channeldata/{chat.get('channel_id')}"):
        os.makedirs(f"data/channeldata/{chat.get('channel_id')}")
    with open(f"data/channeldata/{chat.get('channel_id')}/channel_info.json", "w") as f:
        json.dump({
            "SteamID": chat.get("steamid"),
            "UsersToPing": chat.get("notify")
        }, f, indent=4)