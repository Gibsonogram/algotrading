from binance.client import Client
import requests
from config import *
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
    return usd_pairs


def get_coin_data(coin, interval, start_date, end_date=str(datetime.datetime.today())):
    """
    Gets binance coin/usd data of choice. 
    returns: df of coin data with specified interval, start_date, end_date
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
    # I have found that new coins sometimes cause the next line to fail. They need to have historical klines
    # for to take data from... so we wrap it in a try block.
    try:
        candlesticks = client._historical_klines(coin, interval, start_date, end_date)
        for candlestick in candlesticks:
            candlestick[0] = candlestick[0] / 1000
        data = pd.DataFrame(candlesticks)
        dates = data[0].values
        data = data[[1,4]].astype(float)
        data[0] = [datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%m') for x in dates]
        data.columns = ['Open','Close','Date']
        return data
    except KeyError:
        return


def get_recent_coin_data(coin, interval, candle_limit=202):
    """
    Gets binance coin/usdt data of choice. 
    Unfortunately it needs usdt and it has be websocketed. 
    returns: df of coin data with specified interval, start_date, end_date
    ---------------
    coin: 
    interval: the interval you want the data in
    start_date: Uses a date parser :)
    end_date: Uses a date parser. Defaults to the current time.
    """

    url = 'https://api.binance.com/api/v3/klines'
    params = {
    'symbol': coin,
    'interval': interval,
    'limit': 205}

    data = requests.get(url, params=params).json()
    if len(data) < 3:
        print(data)
        return
    else:
        x = pd.DataFrame()
        transposed = np.transpose(data)
        x['Open'] = transposed[1]
        x['Close'] = transposed[4]
        x = x.astype(float)
        x['Date'] = [float(i) / 1000 for i in transposed[0]]
        x['Date'] = [datetime.datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%m') for i in x['Date'].values]
        return x



def all_coin_data_backtesting(interval, start_date, end_date=str(datetime.datetime.today())):
    """
    Retrieves older candle data, using binance historical klines, rather than websocket. 
    
    """
    df = pd.DataFrame()
    first = True
    for coin in get_usd_coins():
        coin_data = get_coin_data(coin, interval, start_date, end_date)
        # when new coins are listed, they lack history for the kline fxn to pull from, so we check for that.
        if coin_data is not None:
            df[f'{coin}_Open'] = coin_data["Open"]
            df[f'{coin}_Close'] = coin_data['Close']
            #df[f"{coin}_vol"] = coin_data["Volume"]
            if first:
                dates = coin_data["Date"]
                first = False
    df = df.dropna(axis=1, how='any')
    df = df.astype(float)
    df["Date"] = dates
    return df

def all_coin_data(interval, candle_lim=202):
    df = pd.DataFrame()
    first = True
    for coin in get_usd_coins():
        # we add T because the websocket is annoying and only uses tether pairs :|
        coin = coin+'T'
        coin_data = get_recent_coin_data(coin, interval, candle_limit=candle_lim)
        # when new coins are listed, they lack history for the kline fxn to pull from, so we check for that.
        if coin_data is not None:
            coin = coin[:-1]
            df[f'{coin}_Open'] = coin_data["Open"]
            df[f'{coin}_Close'] = coin_data['Close']
            #df[f"{coin}_vol"] = coin_data["Volume"]
            if first:
                dates = coin_data["Date"]
                first = False
    df = df.dropna(axis=1, how='any')
    df = df.astype(float)
    df["Date"] = dates
    return df


#x = all_coin_data('4h', '3 Jan 2022')
#print(x)
#x.to_csv('Binance/opens_1h.csv', index=False)

