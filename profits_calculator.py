import cbpro
from dotenv import dotenv_values
import argparse

parser = argparse.ArgumentParser(description='Calculates the overall profits from limit orders on a product in Coinbase Pro.\nExample:\npython profits_calculator.py ETH-USD')
parser.add_argument('product', type=str, 
                    help='Cryptocurrency product to calculate profits for, e.g. ETH-USD, BTC-USD, MATIC-USD')
parser.add_argument('--quiet', '-q', action='store_true',
                    help='Flag.  If set, runs code in quiet mode.')

args = parser.parse_args()

# Don't use namespaces
product = args.product
quiet = args.quiet

if not quiet:
  print(f"product = {product}")
  print(f"quiet   = {quiet}")

# initialize
config = dotenv_values(".env")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# retrieve current price
order_book = auth_client.get_product_order_book(product)
current_bid = float(order_book['bids'][0][0])
current_ask = float(order_book['asks'][0][0])
current_price = (current_bid + current_ask) / 2

# Get user limit orders
orders = auth_client.get_orders(product, status='all')
list_orders = list(orders)
print(list_orders)

print("\033[92m")
print("Filled Sells")
print("=============")
print("\033[0m", end="")
print("      Value         Fees")
total_sell_value = 0.0
total_sell_fees = 0.0
for order in list_orders:
    if order["status"] == "done":
        if order["side"] == "sell":
            temp_size = float(order["size"]) # in product units, i.e. ETH
            temp_price = round(float(order["price"]), 2) # price at the time of the order fill, in units of product/USD
            temp_fees = round(float(order["fill_fees"]), 2) # USD
            temp_value = round(temp_size * temp_price, 2) # USD, should be the same as order["executed_value"]

            total_sell_value += temp_value
            total_sell_fees += temp_fees

            print(f"{temp_value:7.2f} USD  {temp_fees:7.2f} USD ")

print("\033[91m")
print("Filled Buys")
print("=============")
print("\033[0m", end="")
print("      Value         Fees")
total_buy_value = 0.0
total_buy_fees = 0.0
for order in list_orders:
    if order["status"] == "done":
        if order["side"] == "buy":
            temp_size = float(order["size"]) # in product units, i.e. ETH
            temp_price = round(float(order["price"]), 2) # price at the time of the order fill, in units of product/USD
            temp_fees = round(float(order["fill_fees"]), 2) # USD
            temp_value = round(temp_size * temp_price, 2) # USD, should be the same as order["executed_value"]

            total_buy_value += temp_value
            total_buy_fees += temp_fees

            print(f"{temp_value:7.2f} USD  {temp_fees:7.2f} USD ")

print("\033[92m")
print("Total Sells")
print("-------------")
print("\033[0m", end="")
print("      Value         Fees")
print(f"{total_sell_value:7.2f} USD  {total_sell_fees:7.2f} USD ")

print("\033[91m")
print("Total Buys")
print("-------------")
print("\033[0m", end="")
print("      Value         Fees")
print(f"{total_buy_value:7.2f} USD  {total_buy_fees:7.2f} USD ")

print("\033[96m")
print("Current Price")
print("=============")
print("\033[0m", end="")
print(f"{current_price} USD")
print()

total_profits = total_sell_value - total_buy_value - total_sell_fees - total_buy_fees

print("\033[93m")
print("  Profits")
print("-----------")
print("\033[0m", end="")
print(f"{total_profits:7.2f} USD ")
print()
