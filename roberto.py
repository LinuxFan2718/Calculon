
import cbpro
from dotenv import dotenv_values
import argparse

parser = argparse.ArgumentParser(description='Sets up limit orders for the chosen cryptocurrency product on Coinbase Pro.\nExample:\n')
parser.add_argument('product', type=str, 
                    help='Cryptocurrency product to buy, e.g. ETH-USD, BTC-USD, MATIC-USD')
parser.add_argument('buy_amount_usd', type=float, 
                    help='Amount of crypto to buy in US dollars')
parser.add_argument('swing_percent', type=float, default=5.0,
                    help='Percent to set limit orders above and below.  Must be between 0 and 100.  Default is 5.0')
parser.add_argument('--yes', '-y', action='store_true',
                    help='Flag.  If set, does not need confirmation to set up limit orders.')
parser.add_argument('--quiet', '-q', action='store_true',
                    help='Flag.  If set, runs code in quiet mode.')

args = parser.parse_args()

# Don't use namespaces
product = args.product
buy_amount_usd = args.buy_amount_usd
swing_percent = args.swing_percent
yes = args.yes
quiet = args.quiet

if not quiet:
  print(f"product         = {product}")
  print(f"buy_amount_usd  = {buy_amount_usd}")
  print(f"swing_percent   = {swing_percent}")
  print(f"yes             = {yes}")
  print(f"quiet           = {quiet}")

# Check out user inputs
if swing_percent < 0.0:
  print(f"swing_percent = {swing_percent} is not valid")
elif swing_percent > 100.0:
  print(f"swing_percent = {swing_percent} is not valid")
else:
  swing_size = swing_percent / 100.0

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

# calculate prices
buy_price = round((1 - swing_size) * current_price, 2)
sell_price = round((1 + swing_size) * current_price, 2)

def round_size(product):
  if product == "MATIC-USD":
    return 1
  elif product == 'ETH-USD':
    return 8

# calculate amount, i.e. "size", of crypto to buy, for now the same
buy_amount = round(buy_amount_usd / current_price, round_size(product))
sell_amount = round(buy_amount_usd / current_price, round_size(product))

crypto = product.split('-')[0]
if not quiet:
  print()
  print("\033[93m", end="")
  print(f"{crypto} current price: ${current_price}")
  print("\033[0m", end="")
  print("\033[92m", end="")
  print(f"buy  {product} ${buy_price} ${buy_amount_usd} ({buy_amount} {crypto})")
  print("\033[0m", end="")
  print("\033[91m", end="")
  print(f"sell {product} ${sell_price} ${buy_amount_usd} ({sell_amount} {crypto})")
  print("\033[0m", end="")

if yes:
  ans = 'y'
else:
  print("place limit orders? (y/n)")
  ans = input()

if ans == 'y':
  buy_order = auth_client.place_limit_order(product_id=product,
                                side='buy',
                                price=buy_price,
                                size=buy_amount)

  sell_order = auth_client.place_limit_order(product_id=product,
                                side='sell',
                                price=sell_price,
                                size=sell_amount)

  if 'message' in buy_order:
    print('buy error:', buy_order['message'])
  if 'message' in sell_order:
    print('sell error:', sell_order['message'])
else:
  print(f"orders aborted")

# Pretty print limit orders and current price
def print_order_book():
  orders = auth_client.get_orders()
  list_orders = list(orders)
  print("\033[92m")
  print("Limit Sells")
  print("===========")
  print("\033[0m", end="")
  for order in list_orders:
      if order["side"] == "sell":
          temp_price = round(float(order["price"]), 2)
          temp_diff = round(temp_price - current_price, 2)
          temp_percent_diff = 100 * temp_diff / current_price
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
          temp_percent_diff = 100 * temp_diff / current_price
          print(f"{temp_price}   (\033[91m {temp_diff} \033[0m) (\033[91m {temp_percent_diff:.3f} % \033[0m)")
  print()

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