import os
import cbpro
from dotenv import dotenv_values
import argparse
import datetime

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

###   Functions   ###
def get_datetime_from_utc(utc_date_string):
    """Takes in utc_date_string, like '2021-11-25T22:52:29.119195Z'
    Returns the corresponding datetime object.
    """
    dt = datetime.datetime.strptime(utc_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return dt

def parse_args():
    """Parses the user command line arguments
    """
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

    return product, quiet

def get_list_of_order_ids(product, status='all'):
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
    orders = auth_client.get_orders(product, status=status)
    list_orders = list(orders)
    current_order_list = []
    for order in list_orders:
        if order['product_id'] == product:
            current_order_list.append(order)
    return current_order_list

def get_current_price(product):
    """Gets current price of product on Coinbase pro.

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

    # retrieve current price
    order_book = auth_client.get_product_order_book(product)
    current_bid = float(order_book['bids'][0][0])
    current_ask = float(order_book['asks'][0][0])
    current_price = (current_bid + current_ask) / 2 

    return current_price

def print_filled_orders_info(product, list_orders):
    """Pretty prints the filled limit order information for product
    """
    # retrieve current price
    current_price = get_current_price(product)

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
    print("Total Filled Sells")
    print("-------------")
    print("\033[0m", end="")
    print("      Value         Fees")
    print(f"{total_sell_value:7.2f} USD  {total_sell_fees:7.2f} USD ")

    print("\033[91m")
    print("Total Filled Buys")
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

def process_account_history(account_generator):
    """Processes the generator returned by Coinbase Pro API,
    returning sorted datetimes, account balances, and trade amounts in a dictionary
    auth_client.get_account_history(account_id) returns a generator of your account history.
    This processes that generator to get the data out.

    Input:
    -------
    account_generator: generator
        generator of the account history for one currency on Coinbase Pro

    Output:
    account_history: dictionary
        dictionary with keys of the datetimes, balances, and trade amouths
    """
    datetimes = np.array([])
    balances = np.array([])
    amounts = np.array([])
    for trade in account_generator:
        datetime = get_datetime_from_utc(trade['created_at'])
        balance = float(trade['balance'])
        amount = float(trade['amount'])

        datetimes = np.append(datetime, datetimes)
        balances = np.append(balance, balances)
        amounts = np.append(amount, amounts)

    # sort by time
    indices = np.argsort(datetimes)
    datetimes = datetimes[indices]
    balances = balances[indices]
    amounts = amounts[indices]

    account_history = {}
    account_history['datetimes'] = datetimes
    account_history['balances'] = balances
    account_history['amounts'] = amounts

    return account_history


def plot_user_account_holdings(product):
    """Plots the user account holdings for each part of the product, 
    i.e. if the product is ETH-USD, plots both ETH and USD holdings together.

    Input:
    ------
    product: str
        Cryptocurrency product set limit orders on 
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fig_dir = os.path.join(script_dir, 'figures')
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    # initialize
    config = dotenv_values(".env")
    key = config['API_KEY']
    b64secret = config['API_SECRET']
    passphrase = config['PASSPHRASE']
    auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

    ###   Get user account history   ###
    product_split = product.split('-')
    product_bought = product_split[0]
    product_sold = product_split[1]

    for account in auth_client.get_accounts():
        if account['currency'] == product_bought:
            crypto_id = account['id']
        if account['currency'] == product_sold: # usually USD
            fiat_id = account['id']

    crypto_trades = auth_client.get_account_history(crypto_id)
    fiat_trades = auth_client.get_account_history(fiat_id)

    crypto_history = process_account_history(crypto_trades)
    fiat_history = process_account_history(fiat_trades)

    # Make the plot
    fig, (s1, s2) = plt.subplots(2, sharex=True)
    fig.autofmt_xdate(rotation=45)

    s1.plot(crypto_history['datetimes'], crypto_history['balances'], 'C0', ls='-', marker='o')
    s2.plot(fiat_history['datetimes'], fiat_history['balances'], 'C1', ls='-', marker='o')

    s1.set_title("Account history")
    s1.set_ylabel(f"{product_bought}")
    s2.set_ylabel(f"{product_sold}")
    s2.set_xlabel(f"Dates")

    s1.grid()
    s2.grid()

    plt.tight_layout()
    plot_name = f'account_history_{product_bought}_{product_sold}.pdf'
    full_plot_name = os.path.join(fig_dir, plot_name)
    plt.savefig(full_plot_name)
    print("\nPlot saved at")
    print(full_plot_name)
    print()

if __name__ == "__main__":
    # get user command line arguments
    product, quiet = parse_args()

    # get current order ids 
    list_orders = get_list_of_order_ids(product)

    # print the limit order info
    print_filled_orders_info(product, list_orders)

    # plot user account history
    plot_user_account_holdings(product)

        
