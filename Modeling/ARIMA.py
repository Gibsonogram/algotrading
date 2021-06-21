from pmdarima import auto_arima
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from config import API_SECRET, API_KEY
import csv
from binance.client import Client
from binance.enums import *
from datetime import datetime

plt.figure(figsize=(12,6))


coin = 'REP'
interval = Client.KLINE_INTERVAL_1HOUR
in_sample_forecast_steps = 0
out_sample_forecast_steps = 2
p, d, q = 1,1,1
graph_size = 20
if d == 1:
    variance = -10
else:
    variance = 1




# getting data

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

# these two lines are to shift into my timezone... just so I don't go crazy
dates = dates[:-6]
closes = closes[6:]

real = pd.Series(closes[:-(1+in_sample_forecast_steps)], dates[:-(1+in_sample_forecast_steps)])
real2 = pd.Series(closes, dates)
differenced = real.diff()
differenced = differenced.dropna()



model = ARIMA(differenced, order=(p,d,q))
model_fit = model.fit()

forecast = model_fit.forecast(steps=(1 + in_sample_forecast_steps + out_sample_forecast_steps))

# need some kind of multiplier based on the variance
# moving average of variance
ls = []
for index, val in enumerate(forecast.values):
    if index == 0:
        new = real.values[-1] + (val * variance)
    else:
        new = (val * variance) + ls[-1]
    ls.append(new)
forecast = pd.Series(ls, forecast.index)
forecast = pd.concat([real[-1:], forecast])


plt.plot(real[-graph_size:], color='black', label='real')
plt.plot(forecast, color='red', label='arima forecast')

# this is the one data point that isn't determined yet.
plt.plot(real2[-(in_sample_forecast_steps+2):], color='blue', label='current candle')
plt.legend(loc='best')
plt.title(f'{coin}')
plt.show()
