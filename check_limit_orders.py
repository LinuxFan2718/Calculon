"""check_limit_orders.py

Finds and prints your current limit orders on the current portfolio API in .env

Craig Cahillane
Nov 25, 2021
"""
PRODUCT = "ETH-USD"
BUYSELL = PRODUCT.split("-")
BUY = BUYSELL[0]
SELL = BUYSELL[1]

import cbpro
from dotenv import dotenv_values

# initialize API
config = dotenv_values(".env")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# Get user limit orders
orders = auth_client.get_orders()
list_orders = list(orders)
# print(list_orders)

# retrieve current price
order_book = auth_client.get_product_order_book(PRODUCT)
current_bid = float(order_book['bids'][0][0])
current_ask = float(order_book['asks'][0][0])
current_price = round((current_bid + current_ask) / 2, 2)

print("\033[92m")
print("Limit Sells")
print("===========")
print(" Sell price    Sell size")
print("\033[0m", end="")
for order in list_orders:
    if order["side"] == "sell":
        temp_size = float(order["size"]) 
        temp_price = round(float(order["price"]), 2)
        temp_size_price = round(temp_size * temp_price, 2)
        temp_diff = round(temp_price - current_price, 2)
        temp_percent_diff = 100 * temp_diff / current_price
        print(f"{temp_price:7.2f} USD  {temp_size_price:7.2f} USD  (\033[92m +{temp_diff} \033[0m) (\033[92m {temp_percent_diff:.1f} % \033[0m)")

print("\033[96m")
print("Current Price")
print("=============")
print("\033[0m", end="")
print(f"{current_price} USD")

print("\033[91m")
print("Limit Buys")
print("==========")
print("  Buy price     Buy size")
print("\033[0m", end="")
for order in list_orders:
    if order["side"] == "buy":
        temp_size = float(order["size"]) 
        temp_price = round(float(order["price"]), 2)
        temp_size_price = round(temp_size * temp_price, 2)
        temp_diff = round(temp_price - current_price, 2)
        temp_percent_diff = 100 * temp_diff / current_price
        print(f"{temp_price:7.2f} USD  {temp_size_price:7.2f} USD  (\033[91m {temp_diff} \033[0m) (\033[91m {temp_percent_diff:.1f} % \033[0m)")
print()