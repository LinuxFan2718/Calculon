"""stream_market_data.py
Opens a subscription to real-time market data via Coinbase pro API,
and plots it live using pyqtgraph.
"""
import sys
import time
import json
import cbpro
import datetime
import signal

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from dotenv import dotenv_values

#####   Classes   #####
class MyWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["ETH-USD"]
        self.channels = ["ticker"]
        self.message_count = 0
        self.prices = []
        self.times = []
        self.start_datetime = 0
        # print("Let's count the messages!")
        return

    def on_message(self, data_dict):
        # data_dict = msg #json.dumps(msg, indent=4, sort_keys=True)
        if data_dict["type"] == "ticker":
            temp_price = float(data_dict["price"])

            # Get number of seconds from the first ticker price
            temp_datetime = get_datetime_from_utc(data_dict["time"])
            # Save the first ticker price datetime
            if self.start_datetime == 0:
                self.start_datetime = temp_datetime
            # Compare now vs first ticker price time
            temp_delta_time = temp_datetime - self.start_datetime
            temp_time = temp_delta_time.total_seconds()

            self.prices.append( temp_price )
            self.times.append( temp_time )

        # print(data_dict)
        self.message_count += 1
        return

    def on_close(self):
        print('\033[96m')
        print("Time,\tPrice")
        print('\033[0m')
        for time, price in zip(self.times, self.prices):
            print(f"{time},\t", end='')
            print('\033[92m', end='')
            print(f"{price}", end='')
            print('\033[0m')
        print("-- Goodbye! --")
        return


#####   Functions   #####
def signal_handler(sig, frame):
    print('\033[91m')
    print('You pressed Ctrl+C!')
    print('\033[0m')

    wsClient.close()

    sys.exit(0) 
    return 

def get_datetime_from_utc(utc_date_string):
    """Takes in utc_date_string, like '2021-11-25T22:52:29.119195Z'
    Returns the corresponding datetime object.
    """
    dt = datetime.datetime.strptime(utc_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return dt

def get_orders_dict(orders):
    """Form a dictionary of current order buys and sells
    """
    list_orders = list(orders)
    orders_dict = {}
    orders_dict["sells"] = []
    orders_dict["buys"] = []
    for order in list_orders:
        if order["side"] == "sell":
            temp_price = round(float(order["price"]), 2)
            orders_dict["sells"].append(temp_price)
        if order["side"] == "buy":
            temp_price = round(float(order["price"]), 2)
            orders_dict["buys"].append(temp_price)

    return orders_dict

def init():
    """Initialize matplotlib animation plot.
    """
    ax_list = fig.axes
    ax = ax_list[0]

    # Format plot
    ax.set_title('ETH price [$]')
    ax.set_xlabel('Time [seconds]')
    
    ax.grid()

    line = ax.lines[0]
    line.set_data([], [])
    return line,

def animate(i, xs, ys, orders_dict):
    """Animate the matplotlib plot.
    """
    # print('\033[91m')
    # print(f"xs: {xs}")
    # print(f"ys: {ys}")
    # print('\033[0m')
    try:
        xs_max = max(xs)
        ys_min = min(ys)
        ys_max = max(ys)
    except ValueError:
        xs_max = 1.0

    ax.set_xlim([0.0, xs_max])
    # ax.set_ylim([ys_min, ys_max])

    lines = ax.lines
    main_line = lines[0]
    main_line.set_xdata(xs)
    main_line.set_ydata(ys)

    for line in lines[1:]:
        line.set_xdata([0.0, xs_max])
     
    return main_line,
        

if __name__ == "__main__":

    # initialize API
    config = dotenv_values(".env")
    key = config['API_KEY']
    b64secret = config['API_SECRET']
    passphrase = config['PASSPHRASE']
    auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)

    # Get user limit orders
    orders = auth_client.get_orders()
    orders_dict = get_orders_dict(orders)
    
    # Set up the web socket with coinbase pro
    wsClient = MyWebsocketClient()
    # After creating the class object, we want to register the Ctrl-C signal catcher,
    # which will automatically close the object upon Ctrl-C of the plot
    signal.signal(signal.SIGINT, signal_handler)

    wsClient.start()
    print(wsClient.url, wsClient.products)

    # try:
    #     while True:
    #         print("\nMessageCount =", "%i \n" % wsClient.message_count)
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     wsClient.close()

    # if wsClient.error:
    #     sys.exit(1)
    # else:
    #     sys.exit(0)

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    line, = ax.plot([], [], lw=1.5)

    for buysell, prices in orders_dict.items():
        for jj, price in enumerate(prices):
            if buysell == "sells":
                ax.plot([0.0, 1.0], [price, price], lw=1.5, color="C2", label=f"{buysell} {jj}")
            if buysell == "buys":
                ax.plot([0.0, 1.0], [price, price], lw=1.5, color="C3", label=f"{buysell} {jj}")

    ax.legend(loc='upper left')

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, init_func=init, fargs=(wsClient.times, wsClient.prices, orders_dict), interval=200)
    plt.show()