import datetime
import time
import csgo
import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_inventory_updates(steamid):
    if not os.path.exists(f"data/userdata/{steamid}/inventory_updates.json"):
        return []
    
    with open(f"data/userdata/{steamid}/inventory_updates.json", "r") as f:
        return json.load(f)

def generate_price_graph(price_history, inventory):
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
    # ax.plot(date_plot, price_plot)
    for i in range(1, len(price_plot)):
        if price_plot[i] > price_plot[i-1]:
            color = 'green'
        else:
            color = 'red'
        ax.scatter(date_plot[i], price_plot[i], color=color, s=25, zorder=10)
        ax.plot([date_plot[i-1], date_plot[i]], [price_plot[i-1], price_plot[i]], color=color)
        # ax.text(date_plot[i], price_plot[i], str(round(price_plot[i], 2)), ha='center', va='baseline', color='white', zorder=11, size=16)
        # ax.axvline(x=date_plot[i], color='white', linestyle='--', linewidth=2, zorder=9)
        # ax.text(date_plot[i], 1.01, "Inventory Change", ha='left', va='bottom', color='white', zorder=120, size=12, transform=ax.get_xaxis_transform(), rotation=25)
    
    for update in get_inventory_updates("76561198395558355"):
        ax.axvline(x=datetime.datetime.fromtimestamp(update), color='white', linestyle='--', linewidth=2, zorder=9)
        ax.text(datetime.datetime.fromtimestamp(update), 1.01, "Inventory Change", ha='left', va='bottom', color='white', zorder=120, size=12, transform=ax.get_xaxis_transform(), rotation=25)

    # for i in range(len(date_plot)):
    #     ax.text(date_plot[i], price_plot[i], str(price_plot[i]), ha='center', va='bottom', color='white')
    # for i in range(len(date_plot)):
        # draw point
        # ax.scatter(date_plot[i], price_plot[i], color='', s=10)
        # ax.text(date_plot[i], price_plot[i], str(price_plot[i]), ha='center', va='bottom', color='white')
    ax.set_facecolor('#444444')
    ax.yaxis.set_label("Case Prices")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
    ax.grid(color='#555555', linestyle='-', linewidth=1)
    # plt.xticks(rotation=45)
    plt.savefig('myplot.png', format='png', dpi=120)
    print({date_plot[i].strftime("%B %d %Y %H:%M"): round(price_plot[i], 2) for i in range(len(date_plot))})

with open("data/price_history.json", "r") as f:
    price_history = json.load(f)

with open("data/userdata/76561198395558355/inventory.json", "r") as f:
    inventory = json.load(f)

generate_price_graph(price_history, inventory)