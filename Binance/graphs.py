import matplotlib.pyplot as plt
import pandas as pd
from candle_strategy import *


# getting crypto market info
closes = pd.read_csv('Binance/closes_4h.csv', usecols=range(0,35))
#closes = closes[3000:]

pc_array  =[[] for _ in range(len(closes.columns))]
for ind, col in enumerate(closes.columns):
    for row in closes[col]:
        x = percent_change(closes.iloc[0, ind], row)
        pc_array[ind].append(x)

pc_res = np.transpose(pc_array)
pc_avg = [np.average(i) for i in pc_res]


df = backtest()
dfw = df.loc[:, df.columns != 'sum']

only_one, two_trades = [], []
for ind, i in dfw.iterrows():
    row = i.values
    first, second = False, False
    for entry in row:
        if entry != 0:
            if first == False:
                only_one.append(entry)
                first = True
                two_trades.append([entry, 0])
            else:
                two_trades[-1][1] = entry
                break
    if first == False:
        only_one.append(0)
        two_trades.append([0,0])

two_trades = [round(np.average(i), 2) for i in two_trades]


profit1, profit2, profit3 = [], [], []
prof_1, prof_2, prof_3 = 0,0,0
for i, entry in enumerate(df['sum'].values):
    prof_1 += only_one[i]
    prof_2 += two_trades[i]
    prof_3 += entry
    profit1.append(prof_1)
    profit2.append(prof_2)
    profit3.append(prof_3)

profit3 = [i * 0.2 for i in profit3]


x1, x2, x3 = 250, 300, 350

x = candle_strategy_realism(3, x3)
y = candle_strategy_realism(4, x3)
z = candle_strategy_realism(5, x3)
x_prof, y_prof, z_prof = 0,0,0
x_res, y_res, z_res = [],[],[]
for i in range(0,len(x)):
    x_prof += x[i]
    x_res.append(x_prof)
    y_prof += y[i]
    y_res.append(y_prof)
    z_prof += z[i]
    z_res.append(z_prof)


plt.figure(figsize=(12, 5))
#plt.title('Trading 18 most common usd coins on Binance. 4h chart. Nov. 19 -> Nov. 21')
#plt.plot(pc_avg, label='avg percent increase of coins being traded')
plt.plot(x_res, label=f'3 thread w {round(x1 / 6)} day autosell')
plt.plot(y_res, label=f'4 threads w {round(x2 / 6)} day autosell')
plt.plot(z_res, label=f'5 threads w {round(x3 / 6)} day autosell')
plt.legend(loc='best')

plt.show()
