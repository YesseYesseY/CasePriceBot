import json
import os
import discord
import asyncio
import datetime
import csgo
from discord.ext import tasks, commands
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

default_channel_info = {
    "SteamID": 0,
    "UsersToPing": []
}

default_config = {
    "Token": "",
    "Prefix": "§"
}

def get_inventory(steamid):
    if not os.path.exists(f"data/userdata/{steamid}/inventory.json"):
        if not os.path.exists(f"data/userdata/{steamid}"):
            os.makedirs(f"data/userdata/{steamid}")
        inventory = csgo.get_inventory(steamid)
        if not inventory:
            return None
        
        with open(f"data/userdata/{steamid}/inventory.json", "w") as f:
            json.dump(inventory, f, indent=4)
        return inventory
    
    with open(f"data/userdata/{steamid}/inventory.json", "r") as f:
        return json.load(f)
    
def update_inventory(steamid): # This should not be used yet, it messes up the graph values
    if not os.path.exists(f"data/userdata/{steamid}/inventory.json"):
        return None
    
    inventory = csgo.get_inventory(steamid)
    if not inventory:
        return None
    
    with open(f"data/userdata/{steamid}/inventory.json", "w") as f:
        json.dump(inventory, f, indent=4)

    if not os.path.exists(f"data/userdata/{steamid}/inventory_updates.json"):
        with open(f"data/userdata/{steamid}/inventory_updates.json", "w") as f:
            json.dump([], f, indent=4)

    with open(f"data/userdata/{steamid}/inventory_updates.json", "r") as f:
        inventory_updates = json.load(f)
        inventory_updates.append(datetime.datetime.now().timestamp())
        
    with open(f"data/userdata/{steamid}/inventory_updates.json", "w") as f:
        json.dump(inventory_updates, f, indent=4)

    return inventory

def get_inventory_updates(steamid):
    if not os.path.exists(f"data/userdata/{steamid}/inventory_updates.json"):
        return []
    
    with open(f"data/userdata/{steamid}/inventory_updates.json", "r") as f:
        return json.load(f)
    
def get_case_prices():
    return csgo.get_case_prices()

def get_previous_case_prices():
    if not os.path.exists("data/previous_case_prices.json"):
        previous_case_prices = get_case_prices()
        with open("data/previous_case_prices.json", "w") as f:
            json.dump(previous_case_prices, f, indent=4)
        return previous_case_prices
    
    with open("data/previous_case_prices.json", "r") as f:
        return json.load(f)

def get_config():
    config: dict = {}

    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)

    with open('config.json', 'r') as f:
        config = json.load(f)

    config = default_config | config
    save_config = False
    
    token = config.get('Token')
    if not token: 
        print("No token found in config.json!")
        token = input("Enter token (this will be auto-saved to config.json): ")
        config['Token'] = token

    if save_config:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

    return config

def time_until(Year=None,     Month=None,     Day=None,     Hour=None,     Minute=None,     Second=None,
               AddYear=False, AddMonth=False, AddDay=False, AddHour=False, AddMinute=False, AddSecond=False):
    now = datetime.datetime.now()

    FinalYear = Year if Year is not None and not AddYear else now.year
    FinalMonth = Month if Month is not None and not AddMonth else now.month
    FinalDay = Day if Day is not None and not AddDay else now.day
    FinalHour = Hour if Hour is not None and not AddHour else now.hour
    FinalMinute = Minute if Minute is not None and not AddMinute else now.minute
    FinalSecond = Second if Second is not None and not AddSecond else now.second

    # TODO: Fix error when adding time over 23 hours, 59 minutes, etc.
    if AddYear and Year is not None:
        FinalYear += Year
    if AddMonth and Month is not None:
        FinalMonth += Month
    if AddDay and Day is not None:
        FinalDay += Day
    if AddHour and Hour is not None:
        FinalHour += Hour
    if AddMinute and Minute is not None:
        FinalMinute += Minute
    if AddSecond and Second is not None:
        FinalSecond += Second
        
    then = datetime.datetime(FinalYear, FinalMonth, FinalDay, FinalHour, FinalMinute, FinalSecond)
    return then - now

def get_all_channel_info():
    if not os.path.exists("data/channeldata/"):
        os.makedirs(f"data/channeldata/")
    
    channel_infos = []
    
    for channel in os.listdir("data/channeldata/"):
        if os.path.isdir(f"data/channeldata/{channel}"):
            with open(f"data/channeldata/{channel}/channel_info.json", "r") as f:
                channel_info = json.load(f)
                channel_info_2 = {
                    "ChannelID": int(channel),
                }
                channel_infos.append(channel_info | channel_info_2)
    
    return channel_infos

def get_channel_info(channel_id):
    if not os.path.exists(f"data/channeldata/{channel_id}/channel_info.json"):
        return default_channel_info
    
    with open(f"data/channeldata/{channel_id}/channel_info.json", "r") as f:
        return json.load(f)

def update_channel_info(channel_id, updated_info):
    if not os.path.exists(f"data/channeldata/{channel_id}"):
        os.makedirs(f"data/channeldata/{channel_id}")

    current_info = {}

    if not os.path.exists(f"data/channeldata/{channel_id}/channel_info.json"):
        current_info = default_channel_info
    else:
        with open(f"data/channeldata/{channel_id}/channel_info.json", "r") as f:
            current_info = json.load(f)

    current_info_renewed = default_channel_info | current_info
    
    with open(f"data/channeldata/{channel_id}/channel_info.json", "w") as f:
        json.dump(current_info_renewed | updated_info, f, indent=4)

def generate_inventory_info(inventory: list, current_prices: dict, previous_prices: dict, steamid: int):
    current_total_value = 0
    previous_total_value = 0
    items_info = []
    for item in inventory:
        if not current_prices.get(item):
            continue
        if current_prices.get(item):
            current_total_value += current_prices.get(item)
        if previous_prices.get(item):
            previous_total_value += previous_prices.get(item)
        
    for item in list(set(inventory)): # Remove duplicates
        if not current_prices.get(item):
            continue
        amount = inventory.count(item)
        current_item_price:float = current_prices.get(item)
        previous_item_price:float = previous_prices.get(item)
        total_current_item_price = current_item_price * amount
        total_previous_item_price = previous_item_price * amount

        # Getting highest/lowest price
        if not os.path.exists(f"data/userdata/{steamid}/items/{item}.json"):
            if not os.path.exists(f"data/userdata/{steamid}/items/"):
                os.makedirs(f"data/userdata/{steamid}/items/")
            with open(f"data/userdata/{steamid}/items/{item}.json", "w") as f:
                json.dump(
                    {
                        "HighestPrice": round(previous_item_price, 2), 
                        "LowestPrice": round(previous_item_price, 2),
                        # I'll store the dates but it's not used anywhere yet as i don't know how to make it look nice in an embed
                        "HighestPriceDate": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%d/%m/%Y %H:%M:%S"), 
                        "LowestPriceDate": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%d/%m/%Y %H:%M:%S")
                    }, f, indent=4)
        with open(f"data/userdata/{steamid}/items/{item}.json", "r") as f:
            item_stats = json.load(f)
            highest_price = item_stats.get("HighestPrice")
            lowest_price = item_stats.get("LowestPrice")
        
        if current_item_price > highest_price:
            highest_price = current_item_price
            item_stats["HighestPrice"] = round(highest_price, 2)
            item_stats["HighestPriceDate"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if current_item_price < lowest_price:
            lowest_price = current_item_price
            item_stats["LowestPrice"] = round(lowest_price, 2)
            item_stats["LowestPriceDate"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with open(f"data/userdata/{steamid}/items/{item}.json", "w") as f:
            json.dump(item_stats, f, indent=4)

        item_info = {
            "Name": item,
            "Amount": amount,
            "CurrentPrice": round(current_item_price, 2),
            "PreviousPrice": round(previous_item_price, 2),
            "Difference": {
                "Value": round(abs(current_item_price - previous_item_price), 2),
                "Prefix": "" if current_item_price == previous_item_price else ("+" if current_item_price > previous_item_price else "-")
            },
            "HighestPrice": round(highest_price, 2),
            "LowestPrice": round(lowest_price, 2),
            "HighestPriceDate": item_stats.get("HighestPriceDate"),
            "LowestPriceDate": item_stats.get("LowestPriceDate"),

            "CurrentTotalPrice": round(total_current_item_price, 2),
            "PreviousTotalPrice": round(total_previous_item_price, 2),
            "TotalDifference": {
                "Value": round(abs(total_current_item_price - total_previous_item_price), 2),
                "Prefix": "" if total_current_item_price == total_previous_item_price else ("+" if total_current_item_price > total_previous_item_price else "-")
            },
            "HighestTotalPrice": round(highest_price * amount, 2),
            "LowestTotalPrice": round(lowest_price * amount, 2)
        }
        items_info.append(item_info)

    # Getting highest/lowest total price
    if not os.path.exists(f"data/userdata/{steamid}/inventory_stats.json"):
        if not os.path.exists(f"data/userdata/{steamid}/"):
            os.makedirs(f"data/userdata/{steamid}/")
        with open(f"data/userdata/{steamid}/inventory_stats.json", "w") as f:
            json.dump(
                {
                    "HighestTotalPrice": round(previous_total_value, 2), 
                    "LowestTotalPrice": round(previous_total_value, 2),
                    # I'll store the dates but it's not used anywhere yet as i don't know how to make it look nice in an embed
                    "HighestTotalPriceDate": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%d/%m/%Y %H:%M:%S"), 
                    "LowestTotalPriceDate": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%d/%m/%Y %H:%M:%S")
                }, f, indent=4)
    
    PingUsers = False

    with open(f"data/userdata/{steamid}/inventory_stats.json", "r") as f:
        inventory_stats = json.load(f)
        highest_total_price = inventory_stats.get("HighestTotalPrice")
        lowest_total_price = inventory_stats.get("LowestTotalPrice")

    if current_total_value > highest_total_price:
        highest_total_price = current_total_value
        inventory_stats["HighestTotalPrice"] = round(highest_total_price, 2)
        inventory_stats["HighestTotalPriceDate"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        PingUsers = True
    if current_total_value < lowest_total_price:
        lowest_total_price = current_total_value
        inventory_stats["LowestTotalPrice"] = round(lowest_total_price, 2)
        inventory_stats["LowestTotalPriceDate"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        PingUsers = True

    with open(f"data/userdata/{steamid}/inventory_stats.json", "w") as f:
        json.dump(inventory_stats, f, indent=4)


    return {
        "CurrentTotalPrice": round(current_total_value, 2),
        "PreviousTotalPrice": round(previous_total_value, 2),
        "TotalDifference": {
            "Value": round(abs(current_total_value - previous_total_value), 2),
            "Prefix": "" if current_total_value == previous_total_value else ("+" if current_total_value > previous_total_value else "-")
        },
        "HighestTotalPrice": round(highest_total_price, 2),
        "LowestTotalPrice": round(lowest_total_price, 2),
        "PingUsers": PingUsers,
        "Items": items_info
    }

def generate_basic_info_embed(inventory_info):
    embed = discord.Embed(
        title="Inventory info",
        color=0x00ff00 if inventory_info.get("TotalDifference").get("Prefix") == "+" else 0xff0000 if inventory_info.get("TotalDifference").get("Prefix") == "-" else 0x242424
    )
    embed.set_footer(text="Is your inventory not up to date? Type §updateinv to update it!")

    embed.add_field(name="Current Price", value=f"${inventory_info.get('CurrentTotalPrice')}", inline=False)
    embed.add_field(name="Previous Price", value=f"${inventory_info.get('PreviousTotalPrice')}", inline=False)
    embed.add_field(name="Difference", value=f"{inventory_info.get('TotalDifference').get('Prefix')}${inventory_info.get('TotalDifference').get('Value')}", inline=False)
    embed.add_field(name="Highest Price", value=f"${inventory_info.get('HighestTotalPrice')}", inline=False)
    embed.add_field(name="Lowest Price", value=f"${inventory_info.get('LowestTotalPrice')}", inline=False)

    return embed

def generate_item_info_embed(inventory_info):
    embed = discord.Embed(
        title="Item info",
        color=0x00ff00 if inventory_info.get("TotalDifference").get("Prefix") == "+" else 0xff0000 if inventory_info.get("TotalDifference").get("Prefix") == "-" else 0x242424
    )
    embed.set_footer(text="⚠️ Prices will not always be 100% accurate ⚠️")

    # inline_num = 0
    for item_info in inventory_info.get("Items"):
        field_name = "📈 " if item_info.get("Difference").get("Prefix") == "+" else "📉 " if item_info.get("Difference").get("Prefix") == "-" else ""
        field_name += f"{item_info.get('Name')} ({item_info.get('Amount')})"

        field_value = f"Current Price: ${item_info.get('CurrentPrice')}\n"
        field_value += f"Previous Price: ${item_info.get('PreviousPrice')}\n"
        field_value += f"Difference: {item_info.get('Difference').get('Prefix')}${item_info.get('Difference').get('Value')}\n\n"

        field_value += f"Current Total Price: ${item_info.get('CurrentTotalPrice')}\n"
        field_value += f"Previous Total Price: ${item_info.get('PreviousTotalPrice')}\n"
        field_value += f"Total Difference: {item_info.get('TotalDifference').get('Prefix')}${item_info.get('TotalDifference').get('Value')}\n\n"

        field_value += f"Highest Price: ${item_info.get('HighestPrice')}\n"
        field_value += f"Lowest Price: ${item_info.get('LowestPrice')}\n"

        # inline_num += 1
        # if inline_num % 2 != 0:
        #     embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=field_name, value=field_value, inline=True)

    return embed

def generate_price_graph(price_history, inventory, steamid):
    price_plot = []
    date_plot = []

    for price_data in price_history:
        price_time = datetime.datetime.fromtimestamp(price_data["Time"])
        prices = price_data["Prices"]
        # Filter out stuff from inventory that is not in the prices
        inventory = [item for item in inventory if item in prices]

        total_price_of_inventory = 0

        for item in inventory:
            price = prices[item]
            total_price_of_inventory += price
            
        price_plot.append(total_price_of_inventory)
        date_plot.append(price_time)

    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#333333")
    ax.plot(date_plot, price_plot)
    for i in range(1, len(price_plot)):
        if price_plot[i] > price_plot[i-1]:
            color = 'green'
        else:
            color = 'red'
        ax.scatter(date_plot[i], price_plot[i], color=color, s=25, zorder=10)
        ax.plot([date_plot[i-1], date_plot[i]], [price_plot[i-1], price_plot[i]], color=color)

    for update in get_inventory_updates(steamid):
        ax.axvline(x=datetime.datetime.fromtimestamp(update), color='white', linestyle='--', linewidth=2, zorder=9)
        ax.text(datetime.datetime.fromtimestamp(update), 1.01, "Inventory Change", ha='left', va='bottom', color='white', zorder=120, size=12, transform=ax.get_xaxis_transform(), rotation=25)
    
    ax.set_facecolor('#444444')
    ax.yaxis.set_label("Case Prices")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
    ax.grid(color='#555555', linestyle='-', linewidth=1)
    # plt.xticks(rotation=45)
    plt.savefig(f'data/userdata/{steamid}/price_chart.png', format='png', dpi=120)
    plt.close()
    # return dictionary of date and price
    return {date_plot[i].strftime("%B %d %Y %H:%M"): round(price_plot[i], 2) for i in range(len(date_plot))}

def generate_price_history_embed(price_history, inventory, inventory_info, steamid):
    price_chart_data = generate_price_graph(price_history, inventory, steamid)
    chart_embed = discord.Embed(title="Price Chart", color=0x00ff00 if inventory_info.get("TotalDifference").get("Prefix") == "+" else 0xff0000 if inventory_info.get("TotalDifference").get("Prefix") == "-" else 0x242424)
    chart_embed.set_image(url="attachment://price_chart.png")
    chart_embed.set_footer(text="Do you want the exact data for this chart? Type §chartdata and the bot will send you it!")
    file = discord.File(f"data/userdata/{steamid}/price_chart.png", filename="price_chart.png")
    with open(f"data/userdata/{steamid}/price_chart_data.json", "w") as f:
        json.dump(price_chart_data, f, indent=4)
    price_chart_data_file = discord.File(f"data/userdata/{steamid}/price_chart_data.json", filename="price_chart_data.json")

    return chart_embed, file, price_chart_data_file


if not os.path.exists("data"):
    os.makedirs("data")

# Config
config = get_config()
if not config.get('Token'):
    print("No token found in config.json!")
    exit()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@tasks.loop(hours=1)
async def hourly_update():
    all_channel_info = get_all_channel_info()
    current_prices = get_case_prices()
    if not current_prices:
        print(f"An error occured while fetching current prices!")
        return
    
    previous_prices = get_previous_case_prices()
    if not previous_prices:
        print(f"An error occured while fetching previous prices!")
        return
    
    with open("data/previous_case_prices.json", "w") as f:
        json.dump(current_prices, f, indent=4)
    
    now = datetime.datetime.now()
    if not os.path.exists("data/price_history.json"):
        with open("data/price_history.json", "w") as f:
            json.dump([{
                "Time": datetime.datetime(now.year, now.month, now.day, now.hour - 1, now.minute, now.second, now.microsecond).timestamp(),
                "Prices": previous_prices
            }], f, indent=4)
    with open("data/price_history.json", "r") as f:
        price_history = json.load(f)
    price_history.append({
        "Time": datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond).timestamp(),
        "Prices": current_prices
    })
    with open("data/price_history.json", "w") as f:
        json.dump(price_history, f, indent=4)
    
    for channel_info in all_channel_info:
        steamid = channel_info.get("SteamID")
        if not steamid:
            print(f"Invalid steamid {steamid}!")
            continue

        channelid = channel_info.get("ChannelID")
        channel = client.get_channel(channelid)

        if not channel:
            print(f"Channel {channelid} not found!")
            continue

        print(f"Updating inventory for {steamid} in {channelid}...")

        inventory = get_inventory(steamid)
        if not inventory:
            print(f"An error occured while fetching inventory for {steamid}!")
            continue

        inventory_info = generate_inventory_info(inventory, current_prices, previous_prices, steamid)

        await channel.send(embed=generate_basic_info_embed(inventory_info))
        await channel.send(embed=generate_item_info_embed(inventory_info))
        price_chart_embed, price_chart_file, price_chart_data_file = generate_price_history_embed(price_history, inventory, inventory_info, steamid)
        await channel.send(embed=price_chart_embed, file=price_chart_file)



@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    # §bind <steamid>
    if message.content.startswith("§bind"):
        steamid = message.content.split(" ")[1]
        if not steamid:
            await message.channel.send("Please enter a steamid!")
            return
        
        update_channel_info(message.channel.id, {"SteamID": steamid})

    # §unbind <steamid>
    if message.content.startswith("§unbind"):
        steamid = message.content.split(" ")[1]
        if not steamid:
            await message.channel.send("Please enter a steamid!")
            return
        
        update_channel_info(message.channel.id, {"SteamID": 0})

    # §chartdata
    if message.content.startswith("§chartdata"):
        steamid = get_channel_info(message.channel.id).get("SteamID")
        await message.channel.send(file=discord.File(f"data/userdata/{steamid}/price_chart_data.json", filename="price_chart_data.json"))

    # §updateinv
    # this is for manual updating of the inventory
    # if i do it every hour i will be rate limited
    # this does mess up the prices on the graph
    # ill fix it later with inventory snapshots
    if message.content.startswith("§update"):
        steamid = get_channel_info(message.channel.id).get("SteamID")
        if not steamid:
            await message.channel.send("Please bind a steamid first!")
            return
        
        update = update_inventory(steamid)
        if not update:
            await message.channel.send("An error occured while updating your inventory!")
            return
        
        await message.channel.send(f"Inventory updated!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    if input("Do you want to do the hourly update now? (y/n) ").lower() == "y":
        await hourly_update()
    await asyncio.sleep(time_until(Hour=1, Minute=0, Second=0, AddHour=True).total_seconds())
    hourly_update.start()

client.activity = discord.Activity(type=discord.ActivityType.watching, name="? inventories")
client.run(config.get('Token'))