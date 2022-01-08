import numpy as np
from numpy.core.fromnumeric import ptp
import pandas as pd
from cheap_algos import percent_change
from forex_backtesting import *
import matplotlib.pyplot as plt
from forex_backtesting import backtest



def pc_gain(real_closes, backtest_res):
    """
    Params: 
    --------------
    real_closes: closes of actual asset
    backtest_res: array with entries of form [buy_ind, buy_val, sell_ind, sell_val]
    """
    profits = []
    current = 0
    j = 0
    bought = False
    for i in range(0, backtest_res[-1][2]+1):
        if bought:
            ch = round(percent_change(buy_val, real_closes[i])*50, 3)
            profits.append(current + ch)
        
        # buying
        if i == backtest_res[j][0]:
            buy_val = backtest_res[j][1]
            bought = True
            
        # selling
        if i == backtest_res[j][2]:
            current += ch
            bought = False
            j += 1

        if not bought:
            profits.append(current)
    
    return profits

""" 
avg_spread_fees = 0.05
res = backtest_all()
x = res[0]

x["2avg"] = (x.sum(axis=1) / 3) * (1 - avg_spread_fees)



pcs2 = x["2avg"].values

prof2, prof3 = 0, 0
p2, p3 = [], []
for i in range(0, len(x)):
    prof2 += pcs2[i]*50
    p2.append(prof2)
"""


x1, x2, x3 = 200, 350, 500

x = fx_candle_realism(10, x1)
y = fx_candle_realism(10, x2)
z = fx_candle_realism(10, x3)
#w = fx_candle_realism(6, x4)

x = [i*50 for i in x]
y = [i*50 for i in y]
z = [i*50 for i in z]
#w = [i*100 for i in w]

#y = [i*100 for i in y]
xp, yp, zp, wp = [], [], [], []
xo, yo, zo, wo = 0,0,0,0
for i in range(len(x)):
    xo += x[i]
    yo += y[i]
    zo += z[i]
    #wo += w[i]
    xp.append(xo)
    yp.append(yo)
    zp.append(zo)
    #wp.append(wo)


plt.figure(figsize=(10,5))
plt.plot(xp, label=f'7 threads, {round(x1 / 6)} day autosell')
plt.plot(yp, label=f'9 threads, {round(x2 / 6)} day autosell')
plt.plot(zp, label=f'9 threads, {round(x3 / 6)} day autosell')
#plt.plot(wo, label=f'6 threads, {round(x4 / 6)} day autosell')
plt.title("percent gain of algo, trading all FX pairs")
plt.legend(loc='best')
plt.show()
