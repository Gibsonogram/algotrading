import pandas as pd
import numpy as np
from cheap_algos import *


"""
The problem is you'll have to get vast info about previous indicies for specific pair... 
as you move through all rows 1 by 1...
Solutions: 
- just make the trendinator a sep fxn.
trendinator res is fed into candle strategy, letting it know which currencies to avoid
for what time periods...
or avoid entirely?
If trendinator returns 'ranging' or something like it, then the algo knows to simply skip this BEFORE all the calculations
"""
x = pd.read_csv('Backtesting/closes_4h.csv')


def trendinator(values: list, pc):
    sup = max(values)
    inf = min(values)
    x = np.abs(percent_change(sup, inf))
    if x < pc:
        return 'walker texas'
    else:
        return
ls = []
for col in x.columns:
    closes = x[f'{col}'].values
    t = trendinator(closes, 15)
    if t == 'walker texas':
        ls.append(col)

#print(ls)
        
