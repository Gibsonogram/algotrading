# import websocket
# import json
# import pprint
import pandas as pd
import config
from binance.enums import *
import binance.client
import time

Client = binance.client.Client
MOMENTUM_PERIOD = 2

# this gets the keys from config.py file which is .gitignored for my safety.
client = Client(config.API_KEY, config.API_SECRET, tld='us')


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


"""
def moving_average(values, period):
    if len(values) < period - 1:
        return print('period is longer than the list')
    # we use (period - 1) because index starts at 0
    if len(values) >= period - 1:
        period_sum = 0
        for i in range(0, period):
            period_sum += values[-1 - i]
        mov_av = round(period_sum / period, 4)

    return mov_av
"""


def percent_change(initial, final):
    return round((final - initial) / initial * 100, 3)


new_row = True
in_position = False
buy_coin = ''
buy_column = 0
buy_price = 0
buy_amount = 0

wait_minutes = 15
wait_minutes = 60 * wait_minutes

first_coin_array = coin_prices()
history = pd.DataFrame(first_coin_array)
history = history.transpose()
history = history.drop(1, axis=0)


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):

    global my_order
    try:
        my_order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type)

    except:
        print('buy failed')
        raise Exception


def shaka(betting_money, sell_percent):
    # run the coin_prices fxn and get a price list
    global history
    global in_position
    global wait_minutes

    global buy_coin
    global buy_amount
    global buy_column
    global new_row

    commission_multiplier = 0.99925

    if new_row:
        coin_array = coin_prices()
        price_list = [price for coin, price in coin_array]
        history = history.append([price_list])
        percent_change_ls = []

        if len(history) > MOMENTUM_PERIOD:

            for index, price in enumerate(price_list):

                change = percent_change(history.iat[-2, index], price)
                percent_change_ls.append(change)

            # and now we create false history with the last column having the highest percent change
            momentum_sorted = [j for i, j in sorted(zip(percent_change_ls, history))]
            global false_history
            false_history = history.reindex(columns=momentum_sorted)
            false_history = false_history[false_history.columns[::-1]]

    if len(history) > MOMENTUM_PERIOD:
        # buy logic
        if not in_position:
            # we do this so that next time around it will create a new row.
            new_row = True

            top_coin = false_history.iat[0, 0]
            top_price_change = false_history.iat[len(false_history) - 1, 0]

            # give me the deets of the coin I'm looking at buying
            coin_info = client.get_symbol_info(top_coin)
            coin_filter_info = coin_info['filters']
            lot_size_info = dict(coin_filter_info[2])
            min_qty = float(lot_size_info.get('minQty'))
            min_step = float(lot_size_info.get('stepSize'))

            buy_amount = round((betting_money / top_price_change) * commission_multiplier, 3)
            buy_coin = top_coin
            buy_column = false_history.columns[0]
            print(buy_coin)

            # if the min_step is higher than my buy precision, the order won't go through, so we round it.
            if len(str(min_step)) < len(str(buy_amount)):
                sig_figs = len(str(min_step))
                buy_amount = round(buy_amount, sig_figs - 3)
                print(min_step, buy_amount)

            # actual binance buy
            buy_succeeded = order(SIDE_BUY, buy_amount, symbol=f'{buy_coin}')
            in_position = True

            fills = my_order.get('fills')
            fills = dict(fills[0])
            price = fills.get('price')
            symbol = my_order.get('symbol')
            money = float(my_order.get('cummulativeQuoteQty'))
            quantity = float(my_order.get('executedQty'))

            print(f"order info: paid {money} for {quantity} of {symbol} at a price of {price}")

        # sell logic
        if in_position:
            # find column that I have bought and get details:
            latest_change = percent_change(history.iat[-2, buy_column], history.iat[-1, buy_column])

            if latest_change < sell_percent:
                # sell that shit
                print(f'{buy_coin} went down {latest_change}%')
                sell_price = history.iat[-1, buy_column]
                sell_amount = round(sell_price*buy_amount*commission_multiplier, 3)

                # actual binance sell
                sell_succeeded = order(SIDE_SELL, buy_amount, symbol=f'{buy_coin}')

                fills = my_order.get('fills')
                fills = dict(fills[0])
                price = fills.get('price')
                symbol = my_order.get('symbol')
                money = float(my_order.get('cummulativeQuoteQty'))
                quantity = float(my_order.get('executedQty'))

                print(f"order info: sold {quantity} of {symbol} at a price of {price} for {money}")
                print(f'betting money is now {money}')

                # now we can use recursion. We have sold, so in_pos is false.
                # new_row is set to false, so that we don't make a new row of the history df.
                new_row = False
                in_position = False
                shaka(money, 1)
                return

            print(f'In position, but {latest_change} > {sell_percent}, so we hold.', '\n')
            return


while True:
    shaka(20, 0)
    time.sleep(wait_minutes)
