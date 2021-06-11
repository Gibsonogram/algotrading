from os import write
from binance.helpers import interval_to_milliseconds
import config, csv
from binance.client import Client
from binance.enums import *
import numpy as np
import pandas as pd
import backtrader as bt


client = Client(config.API_KEY, config.API_SECRET, tld='us')


BTC_1_day_testarooni = open("BTC_1_day_testarooni.csv", 'w', newline='')

candlestick_writer = csv.writer(BTC_1_day_testarooni, delimiter=',')
candlesticks = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1DAY, '1 Jan, 2018', '1 May, 2021')

for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

print(len(candlesticks))
BTC_1_day_testarooni.close()


class RSIStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, period=14)

    def next(self):
        if self.rsi < 30 and not self.position:
            self.buy(size=0.1)
        if self.rsi > 70 and self.position:
            self.close()

cerebro = bt.Cerebro()

data = bt.feeds.GenericCSVData(dataname='BTC_1_day_testarooni.csv', dtformat=2)

cerebro.adddata(data)

cerebro.addstrategy(RSIStrategy)

# cerebro.run()

# cerebro.plot()
