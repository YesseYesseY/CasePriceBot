import discord
import asyncio
import datetime
import json
import os
from csgo import SteamManager
from discord.ext import tasks

with open('config.json', 'r') as f:
    config = json.load(f)

token = config.get('Token')
if not token:
    print("No token found in config.json!")
    exit()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def seconds_until_00():
    now = datetime.datetime.now()
    return (60 - now.minute - 1) * 60 + (60 - now.second)

def minutes_until_00():
    now = datetime.datetime.now()
    return 60 - now.minute

def get_inventory_safe(steamid):
    with open(f"inventory_backups/{steamid}.json", "r") as f:
        inventory = json.load(f)

    return inventory

def add_inventory_safe(steamid):
    with open(f"inventory_backups/{steamid}.json", "w") as f:
        inventory = manager.get_inventory(steamid)
        json.dump(inventory, f, indent=4)

def remove_duplicates(inventory):
    return list(dict.fromkeys(inventory))

def get_previous_prices():
    if not os.path.exists("previous_prices.json"):
        with open("previous_prices.json", "w") as f:
            json.dump({}, f, indent=4)
    with open("previous_prices.json", "r") as f:
        previous_prices = json.load(f)

    return previous_prices

def override_previous_prices(prices):
    with open("previous_prices.json", "w") as f:
        json.dump(prices, f, indent=4)
    

chats_to_update = []

def get_chats_to_update():
    print("Getting chats to update...")
    if not os.path.exists("chats_to_update.json"):
        with open("chats_to_update.json", "w") as f:
            json.dump([], f, indent=4)
    with open("chats_to_update.json", "r") as f:
        chats_to_update = json.load(f)

    for chat in chats_to_update:
        print(f"Found chat {chat['channel_id']} with steamid {chat['steamid']}")

    return chats_to_update

def override_chats_to_update(chats_to_update):
    with open("chats_to_update.json", "w") as f:
        json.dump(chats_to_update, f, indent=4)


manager = SteamManager()

def bind_channel(channel_id, steamid):
    chats_to_update.append({'channel_id': channel_id, 'steamid': steamid})

def get_difference_prefix(new_val, prev_val):
    if(new_val == prev_val):
        return ""
    elif(new_val > prev_val):
        return "+"
    else:
        return "-"

@tasks.loop(hours=1)
async def inventory_check():
    print("Inventory Check!")
    prices = manager.get_case_prices()
    previous_prices = get_previous_prices()

    if previous_prices == {}:
        override_previous_prices(prices)
        previous_prices = prices

    for chat in chats_to_update:
        steamid = chat['steamid']
        print(f"Updating {chat['channel_id']} with steamid {steamid}...")
        channel = client.get_channel(chat['channel_id'])
        if not channel:
            print(f"Channel {chat['channel_id']} not found!")
            continue
        inventory = get_inventory_safe(steamid)
        inventory_rd = remove_duplicates(inventory)

        total_value = 0
        total_previous_value = 0
        for item in inventory:
            if(prices.get(item) == None):
                continue
            if(previous_prices.get(item) == None):
                continue
            total_value += prices.get(item)
            total_previous_value += previous_prices.get(item)

        if not os.path.exists(f"inventory_info/{steamid}.json"):
            with open(f"inventory_info/{steamid}.json", "w") as f:
                json.dump({'highest_value': total_previous_value, 'lowest_value': total_previous_value}, f, indent=4)

        with open(f"inventory_info/{steamid}.json", "r") as f:
            inventory_info = json.load(f)

        highest_value = inventory_info.get('highest_value')
        lowest_value = inventory_info.get('lowest_value')

        should_notify = total_value > highest_value or total_value < lowest_value

        if(total_value > highest_value):
            highest_value = total_value
        if(total_value < lowest_value):
            lowest_value = total_value

        with open(f"inventory_info/{steamid}.json", "w") as f:
            json.dump({'highest_value': highest_value, 'lowest_value': lowest_value}, f, indent=4)

        color = 0xff0000

        if(total_value > total_previous_value):
            color = 0x00ff00

        basic_info_embed = discord.Embed()
        basic_info_embed.colour = color

        difference_prefix = get_difference_prefix(total_value, total_previous_value)

        basic_info_embed.add_field(name="Last Price", value=f"${total_previous_value:.2f}", inline=False)
        basic_info_embed.add_field(name="Current Price", value=f"${total_value:.2f}", inline=False)
        basic_info_embed.add_field(name="Difference", value=f"{difference_prefix}${abs(total_value - total_previous_value):.2f}", inline=False)
        basic_info_embed.add_field(name="Highest Price", value=f"${highest_value:.2f}", inline=False)
        basic_info_embed.add_field(name="Lowest Price", value=f"${lowest_value:.2f}", inline=False)

        basic_info_embed.set_footer(text="§notify to get notified when the highest/lowest price changes on this inventory!")

        basic_info_message = ""

        if chat.get('notify') != None:
            for user in chat.get('notify'):
                basic_info_message += f"<@{user}> "

        await channel.send(basic_info_message if should_notify else "", embed=basic_info_embed)

        case_prices_embed = discord.Embed()
        case_prices_embed.colour = color
        case_prices_embed.set_footer(text="⚠️ Prices will never be 100% accurate ⚠️")

        for item in inventory_rd:
            if(prices.get(item) == None):
                continue
            if(previous_prices.get(item) == None):
                continue

            total_value = prices.get(item) * inventory.count(item)
            total_previous_value = previous_prices.get(item) * inventory.count(item)
            difference = prices.get(item) - previous_prices.get(item)
            total_difference = total_value - total_previous_value

            difference_prefix = get_difference_prefix(total_value, total_previous_value)

            item_file_name = item

            if not os.path.exists(f"inventory_info/{steamid}/{item_file_name}.json"):
                # create directory
                if not os.path.exists(f"inventory_info/{steamid}"):
                    os.makedirs(f"inventory_info/{steamid}")

                with open(f"inventory_info/{steamid}/{item_file_name}.json", "w") as f:
                    json.dump({'highest_value': total_previous_value, 'lowest_value': total_previous_value}, f, indent=4)

            with open(f"inventory_info/{steamid}/{item_file_name}.json", "r") as f:
                item_info = json.load(f)

            highest_value = item_info.get('highest_value')
            lowest_value = item_info.get('lowest_value')

            if(total_value > highest_value):
                highest_value = total_value
            if(total_value < lowest_value):
                lowest_value = total_value

            with open(f"inventory_info/{steamid}/{item_file_name}.json", "w") as f:
                json.dump({'highest_value': highest_value, 'lowest_value': lowest_value}, f, indent=4)
            
            field_val = ""
            field_val += f"Previous: ${previous_prices.get(item):.2f}\n"
            field_val += f"Current: ${prices.get(item):.2f}\n"
            field_val += f"Total: ${total_value:.2f}\n"
            field_val += f"Difference: {difference_prefix}${abs(difference):.2f}\n"
            field_val += f"Total Difference: {difference_prefix}${abs(total_difference):.2f}\n"
            field_val += f"Highest Price: ${highest_value:.2f}\n"
            field_val += f"Lowest Price: ${lowest_value:.2f}"

            field_name = ""
            if(total_value > total_previous_value):
                field_name += "📈 "
            elif(total_value < total_previous_value):
                field_name += "📉 "
            
            field_name += f"{item} ({inventory.count(item)})"
            case_prices_embed.add_field(name=field_name, value=field_val, inline=True)

        await channel.send(embed=case_prices_embed)

    override_previous_prices(prices)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await inventory_check()
    await asyncio.sleep(seconds_until_00())
    inventory_check.start()
    
@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith('§bind '):
        for chat in chats_to_update:
            if chat['channel_id'] == message.channel.id:
                await message.channel.send("This channel is already bound to a steamid!")
                return
            
        
        if len(message.content.split(' ')) != 2:
            await message.channel.send("Invalid command! Please use §bind <steamid>")
            return
        
        steamid = message.content.split(' ')[1]
        
        # inform the user if the steamid already is bound to a channel, but dont stop the command
        for chat in chats_to_update:
            if chat['steamid'] == steamid:
                await message.channel.send(f"Warning: {steamid} is already bound to a channel! If you want to unbind a channel use §unbind <steamid>")
                break

        # check if inventory_backups/steamid.json exists
        if not os.path.exists(f"inventory_backups/{steamid}.json"):
            inventory = manager.get_inventory(steamid)
            if not inventory:
                await message.channel.send("Error getting inventory. Error Code: 429")
                return

            with open(f"inventory_backups/{steamid}.json", "w") as f:
                json.dump(inventory, f, indent=4)

        bind_channel(message.channel.id, steamid)
        override_chats_to_update(chats_to_update)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(chats_to_update)} inventories"))

        await message.channel.send(f"Successfully bound channel to {steamid}! Next update will be in {minutes_until_00()} minutes.")

    if message.content.startswith('§unbind'):
        for chat in chats_to_update:
            if chat['channel_id'] == message.channel.id:
                chats_to_update.remove(chat)
                override_chats_to_update(chats_to_update)
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(chats_to_update)} inventories"))
                await message.channel.send("Successfully unbound channel!")
                return
            
    if message.content.startswith('§notify'):
        for chat in chats_to_update:
            if chat['channel_id'] == message.channel.id:
                if chat.get('notify') == None:
                    chat['notify'] = []

                chat.get('notify').append(message.author.id) 
                override_chats_to_update(chats_to_update)
                await message.channel.send(f"Successfully enabled notifications for this inventory!")
                return
        
        await message.channel.send("This channel is not bound to a steamid!")

chats_to_update = get_chats_to_update()
client.activity = discord.Activity(type=discord.ActivityType.watching, name=f"{len(chats_to_update)} inventories")
client.run(token)
