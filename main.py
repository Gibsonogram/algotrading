# import websocket
# import json
import pandas as pd
import numpy as np
import config
from binance.enums import *
import binance.client
import time
# import pprint

Client = binance.client.Client

MOMENTUM_PERIOD = 3
COIN = 'ethusd'
candle_interval = '1m'
coins = []

TRADE_SYMBOL = COIN.upper()
TRADE_QUANTITY = 0.01

# this gets the keys from config.py file which is .gitignored for my safety.
client = Client(config.API_KEY, config.API_SECRET, tld='us')


# in order of params this function says buy/sell quantity of symbol with order type
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        my_order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(my_order)
        print('sending order')
    except:
        return False

    return True


# The following function gets newest price historical_data of the coins I want to check
def coin_prices():
    coin_array = []
    ticker_array = []
    tickers = client.get_all_tickers()

    for ticker in tickers:
        ticker_array.append(list(ticker.values()))
    # I specifically only want the coins that are 'coin/usd'
    for coin, price in ticker_array:
        if coin.count('USD') == 1 and coin[-3:] == 'USD' and coin[-4] != 'B':
            if float(price) <= 1:
                coin_array.append([coin, round(float(price), 4)])
            elif 1 < float(price) < 2:
                coin_array.append([coin, round(float(price), 3)])
            else:
                coin_array.append([coin, round(float(price), 2)])

    return coin_array

momentum_closes = []
in_position = False

first_coin_array = coin_prices()
history = pd.DataFrame(first_coin_array)
history = history.transpose()
history = history.drop(1, axis=0)


def shaka():
    # run the coin_prices fxn and get a price list
    global history
    global in_position

    coin_array = coin_prices()
    price_list = [price for coin, price in coin_array]
    history = history.append([price_list])
    # print(history)
    in_position = False

    for index, price in enumerate(price_list):
        if len(history) > MOMENTUM_PERIOD:
            # the following gets momentum as a percentage and creates a list of them
            coin_momentum = ((price - history.iat[-MOMENTUM_PERIOD, index]) / history.iat[-MOMENTUM_PERIOD, index])*100
            momentum_closes.append(round(coin_momentum, 2))
            if coin_momentum > 1.0:
                print(history.iat[0, index], round(coin_momentum, 2))

    print('no coins have that much momentum')


while True:
    shaka()
    time.sleep(120)
