import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from config import API_SECRET, API_KEY
import csv
from binance.client import Client
from binance.enums import *
from datetime import datetime


# params
coin = 'REP'
interval = Client.KLINE_INTERVAL_1HOUR
p,d,q = 1,1,1


# getting data
client = Client(API_KEY, API_SECRET, tld='us')
coin_data = open(f"historical_data/{coin}_{interval}.csv", 'w', newline='')
candlestick_writer = csv.writer(coin_data, delimiter=',')
candlestick_data = client.get_historical_klines(f'{coin}USD', interval, '1 Mar, 2021')
closes = []
dates = []
for candlestick in candlestick_data:
    candlestick[0] = int(candlestick[0] / 1000)
    candlestick[0] = datetime.utcfromtimestamp(candlestick[0])
    dates.append(candlestick[0])
    closes.append(float(candlestick[4]))
    candlestick_writer.writerow(candlestick)

# these two lines are to shift into my timezone... just so I don't go crazy
dates = dates[:-6]
closes = closes[6:]

real = pd.Series(closes, dates)
differenced = real.diff()
differenced = differenced.dropna()


model = ARIMA(differenced, order=(p,d,q))
model_fit = model.fit()
print(model_fit.summary())


# tests
result = adfuller(differenced)
print(f'ADF stat: {result[0]}')
print(f'p-value : {result[1]}')
for key, value in result[4].items():
    print(f'{key}, {value}')

plot_pacf(differenced.values) # this is for finding p
plot_acf(differenced.values) # this is for finding q
plt.show() 
