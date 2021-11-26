BUY_AMOUNT_USD = 20.0
PRODUCT = "ETH-USD"
SWING_SIZE = 0.01
DEBUG = True

import cbpro
from dotenv import dotenv_values

# initialize
config = dotenv_values(".env")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']
auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# retrieve current price
order_book = auth_client.get_product_order_book(PRODUCT)
current_bid = float(order_book['bids'][0][0])
current_ask = float(order_book['asks'][0][0])
current_price = (current_bid + current_ask) / 2

# calculate prices
buy_price = round((1 - SWING_SIZE) * current_price, 2)
sell_price = round((1 + SWING_SIZE) * current_price, 2)

# calculate amount, i.e. "size", of crypto to buy, for now the same
buy_amount = round(BUY_AMOUNT_USD / current_price, 8)
sell_amount = round(BUY_AMOUNT_USD / current_price, 8)

if DEBUG:
  print(f"buy price      {buy_price} $")
  print(f"current price  {current_price} $")
  print(f"sell price     {sell_price} $")

  product_traded = PRODUCT.split('-')[0]
  print(f"buy amount     {buy_amount} {product_traded}")
  print(f"buy amount     {sell_amount} {product_traded}")

# create limit orders
# Limit order-specific method
buy_order = auth_client.place_limit_order(product_id=PRODUCT, 
                              side='buy', 
                              price=buy_price, 
                              size=buy_amount)

sell_order = auth_client.place_limit_order(product_id=PRODUCT, 
                              side='sell', 
                              price=sell_price, 
                              size=sell_amount)

if 'message' in buy_order:
  print('buy error:', buy_order['message'])
if 'message' in sell_order:
  print('sell error:', sell_order['message'])

orders = auth_client.get_orders()
list_orders = list(orders)
for order in orders:
  print(order)
pass

# sample order
# 'id':'3db19014-f97d-449c-b40e-2122a1d73e50'
# 'price':'1.85090000'
# 'size':'20.00000000'
# 'product_id':'MATIC-USD'
# 'profile_id':'9e90b3fa-499b-4b8a-8bc3-4c4cd1ad6eb2'
# 'side':'buy'
# 'type':'limit'
# 'time_in_force':'GTC'
# 'post_only':False
# 'created_at':'2021-11-26T00:45:18.845641Z'
# 'fill_fees':'0.0000000000000000'
# 'filled_size':'0.00000000'
# 'executed_value':'0.0000000000000000'
# 'status':'open'