"""check_limit_orders.py

Finds and prints your current limit orders on the current portfolio API in .env

Craig Cahillane
Nov 25, 2021
"""

import cbpro
from dotenv import dotenv_values

PRODUCT = "ETH-USD"

# initialize API
config = dotenv_values(".env")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# Get user limit orders
orders = auth_client.get_orders()
list_orders = list(orders)

# retrieve current price
order_book = auth_client.get_product_order_book(PRODUCT)
current_bid = float(order_book['bids'][0][0])
current_ask = float(order_book['asks'][0][0])
current_price = round((current_bid + current_ask) / 2, 2)

print("\033[92m")
print("Limit Sells")
print("===========")
print("\033[0m", end="")
for order in list_orders:
    if order["side"] == "sell":
        temp_price = round(float(order["price"]), 2)
        temp_diff = round(temp_price - current_price, 2)
        temp_percent_diff = temp_diff / current_price
        print(f"{temp_price}   (\033[92m +{temp_diff} \033[0m) (\033[92m {temp_percent_diff:.3f} % \033[0m)")

print("\033[96m")
print("Current Price")
print("=============")
print("\033[0m", end="")
print(current_price)

print("\033[91m")
print("Limit Buys")
print("==========", end="")
print("\033[0m")
for order in list_orders:
    if order["side"] == "buy":
        temp_price = round(float(order["price"]), 2)
        temp_diff = round(temp_price - current_price, 2)
        temp_percent_diff = temp_diff / current_price
        print(f"{temp_price}   (\033[91m {temp_diff} \033[0m) (\033[91m {temp_percent_diff:.3f} % \033[0m)")
print()