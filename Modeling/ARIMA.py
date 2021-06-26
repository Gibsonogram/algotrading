from os import DirEntry
from pandas.core.indexes import period
from pandas.core.indexes.base import ensure_index
from pmdarima import auto_arima
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from config import API_SECRET, API_KEY
import csv
from binance.client import Client
from binance.enums import *
from cheap_algos import *
from datetime import datetime
import numpy as np

plt.figure(figsize=(12,6))


coin = 'BTC'
interval = Client.KLINE_INTERVAL_12HOUR
end_sample = 1
forecast_steps = 1
p, d, q = 21,1,21
graph_size = 20


# getting new data

client = Client(API_KEY, API_SECRET, tld='us')
coin_data = open(f"historical_data/{coin}_{interval}.csv", 'w', newline='')
candlestick_writer = csv.writer(coin_data, delimiter=',')
# we pass in get hist klines with no end date, which will default to the most recent info
candlestick_data = client.get_historical_klines(f'{coin}USD', interval, '1 Jan, 2019')
# returns "generator of T O H L C V values"
closes = []
dates = []
for candlestick in candlestick_data:
    candlestick[0] = int(candlestick[0] / 1000)
    candlestick[0] = datetime.utcfromtimestamp(candlestick[0])
    dates.append(candlestick[0])
    closes.append(float(candlestick[4]))
    candlestick_writer.writerow(candlestick)

"""
# getting old data
coin_data = pd.read_csv(f"historical_data/{coin}_{interval}.csv")
coin_data = pd.DataFrame(coin_data)
closes = coin_data.iloc[:, 4].values
dates = coin_data.iloc[:, 0]
"""
forecast_steps += 1

#USE FOR HOURLY TZ OFFSET
if interval == Client.KLINE_INTERVAL_1HOUR:
    dates = dates[:-6]
    closes = closes[6:]

# remember that the final value of data is not a true candle, its the current price of the asset.
real2 = pd.Series(closes, dates) 
real = pd.Series(closes[:-end_sample], dates[:-end_sample])
differenced = real.diff()
differenced = differenced.dropna()



model = ARIMA(differenced, order=(p,d,q))
model_fit = model.fit()
forecast = model_fit.forecast(steps=forecast_steps)



added_back = []
for index, val in enumerate(model_fit.fittedvalues):
    new_val = val + real.values[index]
    added_back.append(new_val)
model_fit = pd.Series(added_back, index=real.index[:-1])

ls = []
for index, val in enumerate(forecast.values):
    if index == 0:
        new = model_fit.values[-1]
    else:
        new = val + ls[-1]
    ls.append(new)

forecast = pd.Series(ls, index = pd.date_range(start=model_fit.index[-1], periods=len(forecast), freq=interval))




# total error calculation

direction = False
forecast_MAPE = MAPE(forecast.values[-1], real.values[-1])
percent_error = 0
poop = real.values[-50:]
for index, val in enumerate(model_fit.values[-50:]):
    treacherous_snark = MAPE(val, poop[index])
    percent_error += treacherous_snark

print(percent_error)


plt.plot(real2[-graph_size:], color='black', label='real')
plt.plot(model_fit[-10:], color='red', label='model fit')
plt.plot(forecast, color='blue', label='forecast')

plt.legend(loc='best')
plt.title(f'{coin}')
plt.show()
