from numpy.ma.core import append
import numpy as np
from numpy.ma import diff
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller, pacf
from statsmodels.tsa.arima_model import ARIMA
import config
import csv
from binance.client import Client
from binance.enums import *
from datetime import datetime

# plt.figure(figsize=(12,6))


# parameters


coin = 'BTC'
interval = Client.KLINE_INTERVAL_1HOUR
forecast_steps = 0
additional_forecast_steps = 2
p, d, q = 0, 1, 1




# getting data

client = Client(config.API_KEY, config.API_SECRET, tld='us')

coin_data = open(f"historical_data/{coin}_{interval}.csv", 'w', newline='')

candlestick_writer = csv.writer(coin_data, delimiter=',')
# we pass in get hist klines with no end date, which will default to the most recent info
candlestick_data = client.get_historical_klines(f'{coin}USDT', interval, '1 Jan, 2021')
# returns "generator of T O H L C V values"
closes = []
dates = []
for candlestick in candlestick_data:
    candlestick[0] = int(candlestick[0] / 1000)
    candlestick[0] = datetime.utcfromtimestamp(candlestick[0])
    dates.append(candlestick[0])
    closes.append(float(candlestick[4]))
    candlestick_writer.writerow(candlestick)

real = pd.Series(closes, dates)


# stationarizing, differencing, adf

def differencing(series, lag):
    diff_closes = []
    for index, close in enumerate(series):
        if index >= lag:
            diff_close = series[index] - series[index - lag]
            diff_closes.append(diff_close)
        else:
            diff_closes.append(0)
    return diff_closes

differenced = differencing(real.values, 1)
 
differenced = pd.Series(differenced, dates)

# adf, pacf and acf tests
"""
result = adfuller(differenced.values)
print(f'ADF stat: {result[0]}')
print(f'p-value : {result[1]}')
for key, value in result[4].items():
    print(f'{key}, {value}')

plot_pacf(differenced) # this is for finding p
plot_acf(differenced) # this is for finding q
plt.show() 


""" 



# we use this fxn will add back whatever difference we took off
# needed for any model that was differenced for stationarity
def inverse_differencing(prediction_series, original_series):
    diff_added_back = []
    for index, val in enumerate(prediction_series):
        if index >= len(original_series):
            original_series.append(original_series[-1] + val)
        diff_added_back.append(original_series[index] + val)
    return diff_added_back


train = differenced[:-30].values
test = differenced[-30:].values





model = ARIMA(train, order=(8,1,8))





model_fit = model.fit()
start = len(train)
plot_end = len(differenced) - 1 + additional_forecast_steps
pred = model_fit.predict(start=start, end=plot_end)
pred = inverse_differencing(pred, list(real.values[-30:]))


# recombining differences to put ARIMA in original env and plotting
# making a masked array so we can see what steps in the plot are true out-of-sample forecasts
zeroarray = [0] * (len(real.values[-30:]) - forecast_steps)
for _ in range(0, forecast_steps):
    zeroarray.append(1)
my_array = real.values[-30:]
masked = np.ma.array(my_array, mask=zeroarray)


plt.plot(real[-30:].values, color='c', label='real')
# plt.plot(masked, color='m')

plt.plot(pred, color='y', label='ARIMA fit')
# plt.xticks(ticks=ticks)
plt.legend(loc='best')
plt.show()