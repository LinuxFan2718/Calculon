
import cbpro
from dotenv import dotenv_values
import argparse

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
    parser.add_argument('fiat_profits_percent', type=float, default=100.0,
                        help='Percent of profits to keep in fiat.  Must be between 0 and 100.  Default is 100.0')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Flag.  If set, does not need confirmation to set up limit orders.')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Flag.  If set, runs code in quiet mode.')

    args = parser.parse_args()

    # Don't use namespaces
    product = args.product
    buy_amount_usd = args.buy_amount_usd
    swing_percent = args.swing_percent
    fiat_profits_percent = args.fiat_profits_percent
    yes = args.yes
    quiet = args.quiet

    # basic sanitation

    if not quiet:
        print(f"product              = {product}")
        print(f"buy_amount_usd       = {buy_amount_usd}")
        print(f"swing_percent        = {swing_percent}")
        print(f"fiat_profits_percent = {fiat_profits_percent}")
        print(f"yes                  = {yes}")
        print(f"quiet                = {quiet}")

    return product, buy_amount_usd, swing_percent, fiat_profits_percent, yes, quiet


def set_limit_orders(product, buy_amount_usd, swing_percent, fiat_profits_percent, yes, quiet):
    """main function of roberto.py.
    Sets the buy low / sell high limit orders for the cryptocurrency product specified.

    Inputs:
    -------
    product: str
        Coinbase pro cryptocurrency to set limit orders on, e.g. 'ETH-USD', or 'MATIC-USD'
    buy_amount_usd: float
        Central amount of cryptocurrency to trade at the current price, e.g. 1000.0
    swing_percent: float
        Percent amount above and below the current price to set the limit orders at, e.g. 5.0
    fiat_profits_percent: float
        Percent of profits to keep in fiat, e.g. 100.0
    yes: bool
        Flag. If set, user will not need to manually type 'y' to activate limit orders
    quiet: bool
        Flag. If set, does not print so much to terminal.

    Outputs:
    --------
    buy_order: dict
        limit order buy Coinbase pro API information
    sell_order: dict
        limit order sell Coinbase pro API information
    """

    # Check out user inputs
    if swing_percent < 0.0 or swing_percent > 100.0:
        print()
        print(f"swing_percent = {swing_percent} is not valid")
        print("no orders placed")
        return
    else:
        swing_size = swing_percent / 100.0

    if fiat_profits_percent < 0.0 or fiat_profits_percent > 100.0:
        print()
        print(f"fiat_profits_percent = {fiat_profits_percent} is not valid")
        print("no orders placed")
        return
    else:
        ratio_profits_in_fiat = fiat_profits_percent / 100.0

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

    # decide how much profits to keep in crypto versus fiat
    # ratio_profits_in_fiat = 1.0

    # calculate amount, i.e. "size", of crypto to buy, for now the same
    buy_size = round(buy_amount_usd * (1 - ratio_profits_in_fiat * swing_size) / buy_price, round_size(product))
    sell_size = round(buy_amount_usd * (1 + ratio_profits_in_fiat * swing_size) / sell_price, round_size(product))

    crypto = product.split('-')[0]
    if not quiet:
        print()
        print(f"{crypto} current price: ${current_price}")
        print("\033[0m", end="")
        print("\033[92m", end="")
        print(f"buy  {product} ${buy_price} ${buy_price * buy_size} ({buy_size} {crypto})")
        print("\033[0m", end="")
        print("\033[91m", end="")
        print(f"sell {product} ${sell_price} ${sell_price * sell_size} ({sell_size} {crypto})")
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
                                        size=buy_size)

        sell_order = auth_client.place_limit_order(product_id=product,
                                        side='sell',
                                        price=sell_price,
                                        size=sell_size)

        if 'message' in buy_order:
            print('buy error:', buy_order['message'])
        if 'message' in sell_order:
            print('sell error:', sell_order['message'])
    else:
        print(f"orders aborted")
        return 

    return buy_order, sell_order

if __name__ == "__main__":
    product, buy_amount_usd, swing_percent, fiat_profits_percent, yes, quiet = parse_args()
    set_limit_orders(product, buy_amount_usd, swing_percent, fiat_profits_percent, yes, quiet)

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