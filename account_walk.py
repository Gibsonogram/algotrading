import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Backtesting.cheap_algos import percent_change



# params
week_num = 104
starting_capital = 200


weeks = np.arange(0,week_num)
mean_x1, std_x1 = 0.0774, 0.085
mean_x2, std_x2 = 0.0311, 0.076
x1 = np.random.normal(loc=mean_x1, scale=std_x1, size=(2, week_num))
x2 = np.random.normal(loc=mean_x2, scale=std_x2, size=(2, week_num))


""" 

Crypto Momentum strategy

Holding 1 days, Sell_pc = 90%
x_highest: 5
Expected value[week - fees] = 1.76%
Profits 52.4% of the time.
Standard deviation: 0.182
"""

f, g, h, i = [],[],[], []
for week in weeks:
    if week == 0:
        f_st = g_st = h_st = i_st = starting_capital
    else:
        f_st = f_gets
        g_st = g_gets
        h_st = h_gets
        i_st = i_gets

    f_gets = round((f_st)*(1 + x1[0][week]), 3)
    g_gets = round((g_st)*(1 + x1[1][week]), 3)
    h_gets = round((h_st)*(1 + x2[0][week]), 3)
    i_gets = round((i_st)*(1 + x2[1][week]), 3)
    f.append(f_gets)
    g.append(g_gets)
    h.append(h_gets)
    i.append(i_gets)


exp1 = [starting_capital*(1 + mean_x1)**week for week in weeks]



crypto, spy = [],[]
add_amount = 100
for week in weeks:
    if week % 14 == 0:
        starting_capital += add_amount
    crypto.append(starting_capital*(1+mean_x1)**week)
    spy.append(starting_capital*(1+mean_x2)**week)



#annual_crypto_profit = percent_change(crypto[0], crypto[55])
#annual_spy_profit = percent_change(spy[0], spy[55])
#print(spy[55], crypto[55])

plt.figure(figsize=(10,5))
plt.plot(exp1[:56], label='Continuous Crypto Profits')
#plt.plot(spy, label='Continuous SPY profits')
plt.plot(f[:56], label='random walk crypto')
plt.plot(g[:56], label='random walk crypto')
#plt.plot(h, label='random walk SPY')
#plt.plot(i, label='random walk SPY')
plt.legend(loc='best')
plt.show()
