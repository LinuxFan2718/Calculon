BUY_AMOUNT_USD = '10.00'
PRODUCT = "ETH-USD"

import cbpro
from dotenv import dotenv_values
import time

config = dotenv_values(".env")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']

auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# transfer in enough USD
payment_methods = auth_client.get_payment_methods()
# Assume you want to use the first payment method
payment_method = payment_methods[0]

payment_method_id = payment_method['id']
amount = BUY_AMOUNT_USD
currencies = PRODUCT.split("-")
currency_buying = currencies[0]
currency_selling = currencies[1]
currency = "USD"

# https://github.com/danpaquin/coinbasepro-python/blob/5658b2212b0fe39dde18b792f34aeaf81dda6640/cbpro/authenticated_client.py#L798        
result1 = auth_client.deposit(amount, currency, payment_method_id)

def print_dict(dictionary):
    """Prints a dictionary in human-readable format"""
    for key, value in dictionary.items():
        print(f"{key}: {value}")

print()
print_dict(result1)
print("*" * 80)

print("\033[93m")
print(f"Executing purchase of {currency_buying} from {amount} {currency_selling}")
print("\033[0m")

# your account must have enough USD for this to work
# therefore just wait a few seconds before trying then
# have a backoff
time.sleep(10)
buy_made = False
attempts = 0
max_attempts = 3
while(buy_made == False and attempts < max_attempts):
  attempts += 1
  result2 = auth_client.place_market_order(product_id=PRODUCT, 
                                side='buy', 
                                funds=BUY_AMOUNT_USD)
  if 'message' in result2:
    print(result2)
    print("attempts = " + str(attempts) + "/" + str(max_attempts))
    wait_time = 2**attempts
    print("sleeping for " + str(wait_time) + " second(s).")
    time.sleep(wait_time)
  else:
    buy_made = True

print_dict(result2)

print("\033[92m")
print(f"Success!")
print("\033[0m")