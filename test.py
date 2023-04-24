import datetime
import time
import csgo
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    ax.plot(date_plot, price_plot)
    for i in range(1, len(price_plot)):
        if price_plot[i] > price_plot[i-1]:
            color = 'green'
        else:
            color = 'red'
        ax.plot([date_plot[i-1], date_plot[i]], [price_plot[i-1], price_plot[i]], color=color)
    for i in range(len(date_plot)):
        ax.text(date_plot[i], price_plot[i], str(price_plot[i]), ha='center', va='bottom', color='white')
    ax.set_facecolor('#444444')
    ax.yaxis.set_label("Case Prices")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
    # plt.xticks(rotation=45)
    plt.savefig('myplot.png', format='png', dpi=120)

with open("data/price_history.json", "r") as f:
    price_history = json.load(f)

with open("data/userdata/76561198179624574/inventory.json", "r") as f:
    inventory = json.load(f)

generate_price_graph(price_history, inventory)