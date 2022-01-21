BUY_AMOUNT_USD = '25.00'
PRODUCT = "ETH-USD"

import os
import cbpro
from dotenv import dotenv_values
import time
import pprint

def record_start(product, log_dir):
    """Simple function which appends time attempt to create new market orders in dca_within_cbpro_log.txt

    Inputs:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    # file to store when limit orders created
    product_underscore = product.replace('-', '_')
    record_filename = os.path.join(log_dir, f"dca_within_cbpro_log.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"dca_within_cbpro.py run for {product_underscore} at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

def record_success(product, log_dir):
    """Simple function which appends time attempt to create new market orders in dca_within_cbpro_log.txt

    Inputs:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    # file to store when limit orders created
    product_underscore = product.replace('-', '_')
    record_filename = os.path.join(log_dir, f"dca_within_cbpro_log.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"DCA succeeded for {product_underscore} at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

def record_failure(product, log_dir):
    """Simple function which appends time attempt to create new market orders in dca_within_cbpro_log.txt

    Inputs:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    # file to store when limit orders created
    product_underscore = product.replace('-', '_')
    record_filename = os.path.join(log_dir, f"dca_within_cbpro_log.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"DCA failed for {product_underscore} at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

# First, make sure a log/ directory exists
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

record_start(PRODUCT, log_dir)

config = dotenv_values(".env_default")
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']

auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

# # transfer in enough USD
# payment_methods = auth_client.get_payment_methods()
# # Assume you want to use the first payment method
# payment_method = payment_methods[0]

# payment_method_id = payment_method['id']
# amount = BUY_AMOUNT_USD
# currency = "USD"

# # https://github.com/danpaquin/coinbasepro-python/blob/5658b2212b0fe39dde18b792f34aeaf81dda6640/cbpro/authenticated_client.py#L798        
# result1 = auth_client.deposit(amount, currency, payment_method_id)

# pprint.pprint(result1)
# print("*" * 80)

# your account must have enough USD for this to work
# therefore just wait a few seconds before trying then
# have a backoff
# time.sleep(10)
buy_made = False
attempts = 0
max_attempts = 3
while(buy_made == False and attempts < max_attempts):
    attempts += 1
    # https://github.com/danpaquin/coinbasepro-python/blob/5658b2212b0fe39dde18b792f34aeaf81dda6640/cbpro/authenticated_client.py#L381
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

pprint.pprint(result2)

if buy_made:
    record_success(PRODUCT, log_dir)
else:
    record_failure(PRODUCT, log_dir)