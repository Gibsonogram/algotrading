from numpy.ma.core import append
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


# parameters

coin = 'BTC'
x_tick_control = 500
forecast_steps = 3




# getting data

data = pd.read_csv(f'historical_data/Binance_{coin}USDT_1h.csv')


dates = [date[:13] for date in data['date']]
closes = [i for i in data['close']]
real = pd.Series(closes, index=dates)
ticks = [date for index, date in enumerate(dates) if index % x_tick_control == 0]

# creating x_hr chart, bc we are using hourly data
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

# we use this fxn will add back whatever difference we took off
# needed for any model that was differenced for stationarity
def inverse_differencing(prediction_series, original_series):
    diff_added_back = []
    for index, val in enumerate(prediction_series):
        if index >= len(original_series):
            original_series.append(original_series[-1] + val)
        diff_added_back.append(original_series[index] + val)
    return diff_added_back


train = differenced_x_hr[:-30].values
test = differenced_x_hr[-30:].values

model = ARIMA(train, order=(3,1,3))
model_fit = model.fit()

start = len(train)
plot_end = len(x_hr) - 1

pred = model_fit.predict(start=start, end=plot_end)

pred = inverse_differencing(pred, list(x_hr.values[-30:-forecast_steps + 1]))


# recombining differences to put ARIMA in original env and plotting
# making a masked array so we can see what steps in the plot are true out-of-sample forecasts
zeroarray = [0] * (len(x_hr.values[-30:]) - forecast_steps)
for _ in range(0, forecast_steps):
    zeroarray.append(1)
my_array = x_hr.values[-30:]
masked = np.ma.array(my_array, mask=zeroarray)


plt.plot(x_hr.values[-30:], color='c', label='real')
plt.plot(masked, color='m')

plt.plot(pred, color='y', label='ARIMA fit')
# plt.xticks(ticks=ticks)
plt.legend(loc='best')
plt.show()
