from ARIMA.config import API_KEY, API_SECRET
from binance.client import Client
from binance.enums import *
import numpy as np
import pandas as pd
import datetime

client = Client(API_KEY, API_SECRET, tld='us')


def get_usd_coins():
    coin_ls = []
    coin_dicts = client.get_all_tickers()
    for i in coin_dicts:            
        coin = i.get('symbol')
        coin_ls.append(coin)

    usd_pairs = [i for i in coin_ls if i.endswith('USD', -4) and i[-4] != 'B']
    usd_pairs.remove('XRPUSD')
    usd_pairs.remove('USDTUSD')
    usd_pairs.remove('USDCUSD')
    usd_pairs.remove('BUSDUSD')
    
    usd_pairs.append('SHIBUSDT')
    return usd_pairs


def get_coin_data(coin, interval, start_date, end_date=str(datetime.datetime.today())):
    """
    Gets binance coin/usd data of choice. 
    returns: csv of coin data with specified interval, start_date, end_date
    ---------------

    coin: 
    interval: the interval you want the data in
    start_date: Uses a date parser :)
    end_date: Uses a date parser. Defaults to the current time.

    """
    coin = str(coin).upper()
    if coin not in get_usd_coins():
        return "Coin not valid or not on binance."
    valid_intervals = ['1m','3m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d','1w','1M']
    if interval not in valid_intervals:
        return "Interval not valid for binance API. Check valid intervals."
    
    # important to use the _historical_klines and not "get_historical_klines" fxn bc it does not work!
    candlesticks = client._historical_klines(coin, interval, start_date, end_date)
    for candlestick in candlesticks:
        candlestick[0] = candlestick[0] / 1000
        candlestick = candlestick

    data = pd.DataFrame(candlesticks)
    data = data[[0,4]]
    data[0] = [datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%m') for x in data[0]]
    data.columns = ['Date','Close']
    return data


def all_coin_data(interval, start_date, end_date=str(datetime.datetime.today())):
    df = pd.DataFrame()
    for coin in get_usd_coins():
        coin_data = get_coin_data(coin, interval, start_date, end_date)
        df[coin] = coin_data["Close"]
        dates = coin_data["Date"]
    df = df.fillna(0)
    df = df.astype(float)
    df["Date"] = dates
    return df
