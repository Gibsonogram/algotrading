from numpy.lib.npyio import genfromtxt
from numpy.random import seed
import talib as tl
import numpy as np


my_data = np.genfromtxt('BTC_Sep2019_May2021_15min.csv', delimiter=',')

# this data is in the form UOHLC, where U is unix timestamp
# I just want the close of each line, which is the 4th element of each line.

closes = my_data[:, 4]

rsi_closes = tl.RSI(closes, timeperiod=14)

print(rsi_closes)

