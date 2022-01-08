from functools import partial
import requests
import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries


API_key = 'V04NKKQ1INFF2M6Y'
ticker = "SPY"
fxn = ['TIME_SERIES_INTRADAY','TIME_SERIES_INTRADAY_EXTENDED']
interval = ['1min', '5min', '15min', '30min', '60min']


"""
big_tuna = pd.DataFrame()
for i in range(11,13):
    slice = f'year1month{i}'
    data_slice = f'https://www.alphavantage.co/query?function={fxn[1]}&symbol={ticker}&interval={interval[4]}&slice={slice}&apikey={API_key}&datatype=csv&outputsize=full'
    df = pd.read_csv(data_slice)
    big_tuna = big_tuna.append(df)

big_tuna.to_csv('historical_data/spy_hourly2.csv', index=False)
"""
