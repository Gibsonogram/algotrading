from os import write
from binance.helpers import interval_to_milliseconds
import csv
from Modeling.config import API_KEY, API_SECRET
from binance.client import Client
from binance.enums import *
import numpy as np
import pandas as pd

client = Client(API_KEY, API_SECRET, tld='us')

coin = 'ETH'
interval = Client.KLINE_INTERVAL_4HOUR

coin_1_day = open(f"{coin}_{interval}.csv", 'w', newline='')

candlestick_writer = csv.writer(coin_1_day, delimiter=',')
candlesticks = client.get_historical_klines(f'{coin}USDT', interval, '1 Jan, 2021', '1 May, 2021')

for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

