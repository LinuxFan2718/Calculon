"""stream_market_data.py
Opens a subscription to real-time market data via Coinbase pro API,
and plots it live using pyqtgraph.
"""
import sys
import time
import json
import cbpro


#####   Classes   #####
class MyWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["ETH-USD"]
        self.channels = ["ticker"]
        self.message_count = 0
        print("Let's count the messages!")

    def on_message(self, msg):
        print(json.dumps(msg, indent=4, sort_keys=True))
        self.message_count += 1

    def on_close(self):
        print("-- Goodbye! --")


wsClient = MyWebsocketClient()
wsClient.start()
print(wsClient.url, wsClient.products)
try:
    while True:
        print("\nMessageCount =", "%i \n" % wsClient.message_count)
        time.sleep(1)
except KeyboardInterrupt:
    wsClient.close()

if wsClient.error:
    sys.exit(1)
else:
    sys.exit(0)