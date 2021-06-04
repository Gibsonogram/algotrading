from sklearn.linear_model import LinearRegression
import numpy as np
from numpy.ma import diff
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.stattools import adfuller

plt.figure(figsize=(12,6))

coin = 'BTC'
x_tick_control = 500
data = pd.read_csv(f'historical_data/Binance_{coin}USDT_1h.csv')

dates = [date[:13] for date in data['date']]
closes = [i for i in data['close']]
real = pd.Series(closes, index=dates)
ticks = [date for index, date in enumerate(dates) if index % x_tick_control == 0]

# stationarizing with lag1 differencing
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
# this is equivalent to differencing around 1 day

diff_real = pd. Series(differenced, dates)
""" 
result = adfuller(diff_real.values)
print(f'ADF stat: {result[0]}')
print(f'p-value : {result[1]}')
for key, value in result[4].items():
    print(f'{key}, {value}') """

df1 = pd.DataFrame()
og = pd.DataFrame()
og['closes'] = real.values
og['shifted'] = og['closes'].shift(1)
df1['Differenced'] = differenced
df1['Diff_shifted'] = df1['Differenced'].shift(1)
og, df1 = og.dropna(), df1.dropna()


y = og['closes'].values
X = og['shifted'].values

train_size = int(len(X)*0.7)

X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

X_train = X_train.reshape(-1,1)
X_test = X_test.reshape(-1,1)

lr = LinearRegression()
lr.fit(X_train, y_train)

y_pred = lr.predict(X_test)


plt.plot(y_test[-50:], color='black', label='actual')
plt.plot(y_pred[-50:], color='blue', label='predicted')
# plt.xticks(ticks=ticks)
plt.legend(loc='best')
plt.show()
