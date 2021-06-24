from pandas.core.indexes import period
from pmdarima import auto_arima
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats.stats import moment
from statsmodels.tsa.arima.model import ARIMA
from config import API_SECRET, API_KEY
import csv
from binance.client import Client
from binance.enums import *
from cheap_algos import *
from datetime import datetime
from numpy.ma.core import append
import numpy as np
from numpy.ma import diff
import math

plt.figure(figsize=(12,6))


coin = 'BTC'
interval = Client.KLINE_INTERVAL_12HOUR
in_sample_forecast_steps = 0
out_sample_forecast_steps = 1
p, d, q = 12,1,12
graph_size = 10
factor=3


# getting new data

client = Client(API_KEY, API_SECRET, tld='us')
coin_data = open(f"historical_data/{coin}_{interval}.csv", 'w', newline='')
candlestick_writer = csv.writer(coin_data, delimiter=',')
# we pass in get hist klines with no end date, which will default to the most recent info
candlestick_data = client.get_historical_klines(f'{coin}USD', interval, '1 Mar, 2021')
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

# getting easy data
coin_data = pd.read_csv(f"historical_data/{coin}_{interval}.csv")
coin_data = pd.DataFrame(coin_data)
closes = coin_data.iloc[:, 4].values
dates = coin_data.iloc[:, 0]
"""

# these two lines are to shift into my timezone... just so I don't go crazy
dates = dates[:-6]
closes = closes[6:]

real = pd.Series(closes[:-(1+in_sample_forecast_steps)], dates[:-(1+in_sample_forecast_steps)])
# real.index = pd.DatetimeIndex.date(real.index).to_period('H')

real2 = pd.Series(closes, dates)

differenced = real.diff()
differenced = differenced.dropna()


model = ARIMA(differenced, order=(p,d,q))
model_fit = model.fit()

forecast = model_fit.forecast(steps=3)

# this 'factor' business is kind of insane, but it makes everything work so don't touch it.
# I think because of the differencing, it must be negative.
if d == 1:
    differenced_cumsum = differenced.values.cumsum()
    factor = round(real.values[-1] / differenced_cumsum[-1], 2)
    if factor > 0:
        factor = -factor
else:
    factor = 1

mom = momentum(real[-12:-1])
factor = factor * math.sqrt(mom)
print(factor)
# need some kind of multiplier based on the variance
# moving average of variance
ls = []
for index, val in enumerate(forecast.values):
    if index == 0:
        new = real.values[-1] + (val * factor)
    else:
        new = (val * factor) + ls[-1]
    ls.append(new)

forecast = pd.Series(ls, index = pd.date_range(start=real.index[-1], periods=len(forecast)+1, freq='D', closed='right'))
forecast = pd.concat([real[-1:], forecast])


plt.plot(real2[-graph_size:-1], color='black', label='real')
plt.plot(forecast, color='red', label='arima forecast')

# this is the one data point that isn't determined yet.
plt.plot(real2[-2:], color='blue', label='current candle')
plt.legend(loc='best')
plt.title(f'{coin}')
plt.show()
