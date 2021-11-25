BUY_AMOUNT_USD = '20.00'
PRODUCT = "MATIC-USD"
SWING_SIZE = 0.05

import cbpro
from dotenv import dotenv_values
import time


# initialize
config = dotenv_values(".env")
key = config['BEGINNER_API_KEY']
b64secret = config['BEGINNER_API_SECRET']
passphrase = config['BEGINNER_PASSPHRASE']
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# retrieve current price
order_book = auth_client.get_product_order_book(PRODUCT)
current_bid = float(order_book['bids'][0][0])
current_ask = float(order_book['asks'][0][0])
current_price = (current_bid + current_ask) / 2

# calculate prices
buy_price = (1 - SWING_SIZE) * current_price
sell_price = (1 + SWING_SIZE) * current_price

print("buy price    ", buy_price)
print("current price", current_price)
print("sell price   ", sell_price)
