import os
import time
import cbpro
from dotenv import dotenv_values
import argparse

from roberto import set_limit_orders

def parse_args():
    """Parses the user command line arguments
    """
    parser = argparse.ArgumentParser(description='Sets up limit orders for the chosen cryptocurrency product on Coinbase Pro.\nExample:\npython roberto.py ETH-USD 1000.0 5.0')
    parser.add_argument('product', type=str, 
                        help='Cryptocurrency product to buy, e.g. ETH-USD, BTC-USD, MATIC-USD')
    parser.add_argument('buy_amount_usd', type=float, 
                        help='Amount of crypto to buy in US dollars')
    parser.add_argument('swing_percent', type=float, default=5.0,
                        help='Percent to set limit orders above and below.  Must be between 0 and 100.  Default is 5.0')
    # parser.add_argument('--yes', '-y', action='store_true',
    #                     help='Flag.  If set, does not need confirmation to set up limit orders.')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Flag.  If set, runs code in quiet mode.')

    args = parser.parse_args()

    # Don't use namespaces
    product = args.product
    buy_amount_usd = args.buy_amount_usd
    swing_percent = args.swing_percent
    # yes = args.yes
    quiet = args.quiet

    if not quiet:
        print(f"product         = {product}")
        print(f"buy_amount_usd  = {buy_amount_usd}")
        print(f"swing_percent   = {swing_percent}")
        # print(f"yes             = {yes}")
        print(f"quiet           = {quiet}")

    return product, buy_amount_usd, swing_percent, quiet

def check_if_limits_executed():
    """Function which checks if any limit orders have executed 
    since the last time this script was run.
    It checks by looking at the order ids in the file current_order_ids.txt,
    and comparing to the current active orders.
    If any have executed, they'll be gone from the active orders,
    and we'll return True.
    """
    # create boolean which will be returned by this func
    should_new_orders_be_created = False

    # put order ids in .txt file that will be checked each time cron runs
    cron_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_order_ids.txt")

    # initialize
    config = dotenv_values(".env")
    key = config['API_KEY']
    b64secret = config['API_SECRET']
    passphrase = config['PASSPHRASE']
    auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

    # get the current order ids
    orders = auth_client.get_orders()
    list_orders = list(orders)
    current_order_ids = []
    for order in list_orders:
        temp_id = order["id"]
        current_order_ids.append(temp_id)

    # read in contents of cron_filename to get old order ids
    try:
        with open(cron_filename, "r") as file1:
            temp_order_ids = file1.readlines()
        old_order_ids = []
        for order_id in temp_order_ids:
            old_order_ids.append(order_id.strip('\n'))

    except FileNotFoundError:
        print(f"File not found: cron_filename = {cron_filename} ")
        print(f"Creating file with order ids for next time this script is called.")
        print(f"No new orders will be created.")
        with open(cron_filename, "w") as file1:
            for order_id in current_order_ids:
                file1.write(f"{order_id}\n")
        
        return False # new orders should not be created

    # compare the order ids by sorting and using ==
    old_order_ids.sort()
    current_order_ids.sort()
    if old_order_ids == current_order_ids:
        print("The order ids lists are identical")
        should_new_orders_be_created = False
    else:
        print("The order ids lists are not identical")
        should_new_orders_be_created = True

    return should_new_orders_be_created

def record_new_limit_orders():
    """Simple function which appends time of new limit orders to the end of limit_orders_record.txt,
    and records all the new limit order ids in the current_order_ids.txt.
    """
    # file to store when limit orders created
    record_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "limit_orders_record.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"New limit orders created at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

    # initialize
    config = dotenv_values(".env")
    key = config['API_KEY']
    b64secret = config['API_SECRET']
    passphrase = config['PASSPHRASE']
    auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

    # get the current order ids
    orders = auth_client.get_orders()
    list_orders = list(orders)
    current_order_ids = []
    for order in list_orders:
        temp_id = order["id"]
        current_order_ids.append(temp_id)

    # put order ids in .txt file that will be checked each time cron runs   
    cron_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_order_ids.txt")
    with open(cron_filename, "w") as file1:
        for order_id in current_order_ids:
            file1.write(f"{order_id}\n")

    return

def record_failure():
    """Simple function which appends time attempt to create new limit orders in limit_orders_record.txt
    """
    # file to store when limit orders created
    record_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "limit_orders_record.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"Failed at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

    return

if __name__ == "__main__":
    # If limit orders have been executed, 
    # we want to create new ones using roberto.set_limit_orders() function
    if check_if_limits_executed():
        # In this case, we don't want to ask for user input 
        # because we want to use cron to run this script every minute
        yes = True
        product, buy_amount_usd, swing_percent, quiet = parse_args()

        # use roberto.set_limit_orders function
        set_limit_orders(product, buy_amount_usd, swing_percent, yes, quiet)

        # record the new limit orders in the .txt file
        record_new_limit_orders()

        if not quiet:
            print()
            print("cron_roberto.py is done setting new limit orders!")
            print()

    else:
        record_failure()