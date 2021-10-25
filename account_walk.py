import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from cheap_algos import percent_change


# params
week_num = 104
starting_capital = 500


weeks = np.arange(0,week_num)
mean_x1, std_x1 = 0.0274, 0.299
mean_x2, std_x2 = 0.0224, 0.227
x1 = np.random.normal(loc=mean_x1, scale=std_x1, size=(2, week_num))
x2 = np.random.normal(loc=mean_x2, scale=std_x2, size=(2, week_num))

""" 
x1:
Holding 1 days, Sell_pc = 90%
x_highest: 4
Expected value[week - fees] = 2.35%
Profits 52.0% of the time.
Standard deviation: 0.232

x2:
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


exp1 = [starting_capital*(1+mean_x1)**week for week in weeks]
#exp2 = [starting_capital*(1+mean_x2)**week for week in weeks]


plt.figure(figsize=(10,5))
plt.plot(exp1, label='Continuous x1')
#plt.plot(exp2, label='Continuous x2')
plt.plot(f, label='random x1')
plt.plot(g, label='random x1')
#plt.plot(h, label='random x2')
#plt.plot(i, label='random x2')

plt.legend(loc='best')
plt.show()
