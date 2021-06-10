from pandas.core.indexes.base import Index
from sklearn.linear_model import LinearRegression
import numpy as np
from numpy.ma import diff
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller, pacf
from statsmodels.tsa.arima_model import ARIMA

plt.figure(figsize=(12,6))

# getting data

coin = 'BTC'
x_tick_control = 500
data = pd.read_csv(f'historical_data/Binance_{coin}USDT_1h.csv')

dates = [date[:13] for date in data['date']]
closes = [i for i in data['close']]
real = pd.Series(closes, index=dates)
ticks = [date for index, date in enumerate(dates) if index % x_tick_control == 0]

x = 4
x_hr = real.iloc[::x]






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

differenced_x_hr = differencing(x_hr.values, 1)
 
differenced = pd.Series(differenced, dates)
differenced_x_hr = pd.Series(differenced_x_hr, x_hr.index)

""" 
result = adfuller(differenced_x_hr)
print(f'ADF stat: {result[0]}')
print(f'p-value : {result[1]}')
for key, value in result[4].items():
    print(f'{key}, {value}')
"""








# Model

train = differenced_x_hr[:-30].values
test = differenced_x_hr[-30:].values


model = ARIMA(train, order=(3,1,3))
model_fit = model.fit()

pred = model_fit.predict()




# recombining differences to put ARIMA in original env and plotting

# forecast = function(fxn that differences back)

new_pred = []
for index, val in enumerate(x_hr.values[-30:]):
    new_pred.append(pred[index] + val)


plt.plot(x_hr.values[-30:], label='real')
plt.plot(new_pred, label='ARIMA fit')
# plt.xticks(ticks=ticks)
plt.legend(loc='best')
plt.show()
