"""stream_market_data.py
Opens a subscription to real-time market data via Coinbase pro API,
and plots it live using pyqtgraph.
"""
import sys
import time
import json

import cbpro

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('pyqtgraph example: Scrolling Plots')


#####   Classes   #####
class MyWebsocketClient(cbpro.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.pro.coinbase.com/"
        self.products = ["ETH-USD"]
        self.channels = ["ticker"]
        self.message_count = 0
        self.times = []
        self.prices = []
        print("Let's count the messages!")

    def on_message(self, msg):
        print(json.dumps(msg, indent=4, sort_keys=True))
        self.message_count += 1

        cur_price = msg["price"]
        cur_datetime = msg["time"]
        cur_gpstime = gpstime.gpstime.parse(cur_datetime).gps()

        self.prices.append(cur_price)
        self.times.append(cur_gpstime)

    def on_close(self):
        print("-- Goodbye! --")


wsClient = MyWebsocketClient()
wsClient.start()
print(wsClient.url, wsClient.products)

# Set up the plot window
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle(f'Scrolling {wsClient.products}')

startTime = pg.ptime.time()
chunkSize = 100
maxChunks = 10

p5 = win.addPlot()
p5.setLabel('left', 'Price', '$')
p5.setLabel('bottom', 'Time', 's')
p5.setXRange(-10, 0)
curves = []
data5 = np.empty((chunkSize+1,2))
ptr5 = 0

def update():
    global p5, data5, ptr5, curves
    now = pg.ptime.time()
    for c in curves:
        c.setPos(-(now-startTime), 0)
    
    i = ptr5 % chunkSize
    if i == 0:
        curve = p5.plot()
        curves.append(curve)
        last = data5[-1]
        data5 = np.empty((chunkSize+1,2))        
        data5[0] = last
        while len(curves) > maxChunks:
            c = curves.pop(0)
            p5.removeItem(c)
    else:
        curve = curves[-1]
    data5[i+1,0] = wsClient.times[-1]
    data5[i+1,1] = wsClient.prices[-1]
    curve.setData(x=data5[:i+2, 0], y=data5[:i+2, 1])
    ptr5 += 1

# update all plots
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

if __name__ == '__main__':
    pg.exec()

