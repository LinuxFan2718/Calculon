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

def get_list_of_order_ids(product):
    """Simple function which gets all open limit orders from Coinbase pro API.

    Input:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
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
        if order['product_id'] == product:
            temp_id = order['id']
            current_order_ids.append(temp_id)
    return current_order_ids

def check_if_limits_executed(product):
    """Function which checks if any limit orders have executed 
    since the last time this script was run.
    It checks by looking at the order ids in the file current_order_ids.txt,
    and comparing to the current active orders.
    If any have executed, they'll be gone from the active orders,
    and we'll return True.

    Input:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    # create boolean which will be returned by this func
    should_new_orders_be_created = False

    # get list of current order ids
    current_order_ids = get_list_of_order_ids(product)

    # put order ids in .txt file that will be checked each time cron runs
    product_underscore = product.replace('-', '_')
    cron_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"current_order_ids_{product_underscore}.txt")

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
        print()
        print("old_order_ids:")
        for order_id in old_order_ids:
            print(order_id)
        print()
        print("current_order_ids:")
        for order_id in current_order_ids:
            print(order_id)
        print()
        should_new_orders_be_created = True

        # overwrite old list of order ids, 
        # so we can append new order ids later in record_new_limit_orders()
        with open(cron_filename, "w") as file1:
            for order_id in current_order_ids:
                file1.write(f"{order_id}\n")

    return should_new_orders_be_created

def record_new_limit_orders(product, buy_order, sell_order):
    """Simple function which appends time of new limit orders to the end of limit_orders_record.txt,
    and records all the new limit order ids in the current_order_ids_{product}.txt.

    Inputs:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    buy_order: dict
        limit order buy Coinbase pro API information
    sell_order: dict
        limit order sell Coinbase pro API information
    """
    product_split = product.split('-')
    product_bought = product_split[0]
    product_sold = product_split[1]

    # file to store when limit orders created
    product_underscore = product.replace('-', '_')
    record_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"limit_orders_record_{product_underscore}.txt")

    buy_succeeded = True
    sell_succeeded = True
    with open(record_filename, "a") as file1:
        file1.write(f"\n\nNew limit orders creation attempt at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

        if 'message' in buy_order:
            file1.write(f"\nbuy error: {buy_order['message']}\n")
            buy_succeeded = False
        else:
            file1.write(f"\nLimit buy:\n")
            file1.write(f"Price: {buy_order['price']}\n")
            file1.write(f"Size: {buy_order['size']} {product_bought} ({float(buy_order['price']) * float(buy_order['size'])} {product_sold})\n")
            file1.write(f"ID: {buy_order['id']}\n")

        if 'message' in sell_order:
            file1.write(f"\nsell error: {sell_order['message']}\n")
            sell_succeeded = False
        else:
            file1.write(f"\nLimit sell:\n")
            file1.write(f"Price: {sell_order['price']}\n")
            file1.write(f"Size: {sell_order['size']} {product_bought}  ({float(sell_order['price']) * float(sell_order['size'])} {product_sold})\n")
            file1.write(f"ID: {sell_order['id']}\n")

    # append new order ids to .txt
    cron_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"current_order_ids_{product_underscore}.txt")
    with open(cron_filename, "a") as file1:
        if buy_succeeded:
            file1.write(f"{buy_order['id']}\n")
        if sell_succeeded:
            file1.write(f"{sell_order['id']}\n")

    return

def record_failure(product):
    """Simple function which appends time attempt to create new limit orders in failure_log_{product}.txt

    Inputs:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    # file to store when limit orders created
    product_underscore = product.replace('-', '_')
    record_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"failure_log_{product_underscore}.txt")
    with open(record_filename, "a") as file1:
        file1.write(f"No new limit orders set at {time.strftime('%Y %m %d, %H:%M:%S') }\n")

    return

if __name__ == "__main__":
    # In this case, we don't want to ask for user input     
    # because we want to use cron to run this script every minute
    yes = True
    product, buy_amount_usd, swing_percent, quiet = parse_args()
    # If limit orders have been executed, 
    # we want to create new ones using roberto.set_limit_orders() function
    if check_if_limits_executed(product):
        
        # use roberto.set_limit_orders function
        buy_order, sell_order = set_limit_orders(product, buy_amount_usd, swing_percent, yes, quiet)

        # record the new limit orders in the .txt file
        record_new_limit_orders(product, buy_order, sell_order)

        if not quiet:
            print()
            print("cron_roberto.py is done setting new limit orders!")
            print()

    else:
        record_failure(product)