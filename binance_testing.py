from os import write
from binance.helpers import interval_to_milliseconds
import config, csv
from binance.client import Client
from binance.enums import *
import numpy as np
import pandas as pd


client = Client(config.API_KEY, config.API_SECRET, tld='us')

BTC_candles_15 = open("BTC_2017_2021_15min.csv", 'w', newline='')
candlestick_writer = csv.writer(BTC_candles_15, delimiter=',')


candlesticks = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_15MINUTE, '28 April, 2021', '1 May, 2021')

for candlestick in candlesticks:
    candlestick_writer.writerow(candlestick)

print(len(candlesticks))
BTC_candles_15.close()