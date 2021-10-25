# import websocket
# import json
# import pprint
import pandas as pd
import config
from binance.enums import *
import binance.client
import time

Client = binance.client.Client
MOMENTUM_PERIOD = 5
wait_minutes = 1
starting_money = 100
sell_perc = 0

# this gets the keys from config.py file which is .gitignored for my safety.
client = Client(config.API_KEY, config.API_SECRET, tld='us')

""" 
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


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):

    global my_order
    try:
        my_order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type)

    except:
        print('buy failed')
        raise Exception

"""
real_trading = False

new_row = True
in_position = False
buy_coin = ''
buy_column = 0
buy_price = 0
buy_amount = 0
wait_minutes = 60 * wait_minutes
""" 
#first_coin_array = coin_prices()
history = pd.DataFrame(first_coin_array)
history = history.transpose()
history = history.drop(1, axis=0)
false_history = pd.DataFrame()
 """
""" 
def shaka(betting_money, sell_percent):
    # run the coin_prices fxn and get a price list
    global history
    global in_position
    global wait_minutes
    global false_history

    global buy_coin
    global buy_amount
    global buy_column
    global new_row

    commission_multiplier = 0.99925

    #if len(history) > 10:
     #   history = history.tail(6)
      #  false_history = false_history.tail(6)

    if new_row:
        coin_array = coin_prices()
        price_list = [price for coin, price in coin_array]
        history = history.append([price_list])
        percent_change_ls = []
        mov_ls = []

        # moving average and percent change calculation
        if len(history) > MOMENTUM_PERIOD:

            for index, price in enumerate(price_list):

                # most recent percent change of each coin
                change = percent_change(history.iat[-2, index], price)
                percent_change_ls.append(change)

                # most recent moving average of each coin
                mov_changes = [history.iat[-MOMENTUM_PERIOD + i, index] for i in range(0, MOMENTUM_PERIOD)]
                mov = moving_average(mov_changes, MOMENTUM_PERIOD)
                mov_ls.append(mov)

            # and now we create false history with the last column having the highest percent change
            percent_sorted = [j for i, j in sorted(zip(percent_change_ls, history))]
            # momentum_sorted = [j for i, j in sorted(zip(mov_ls, history))]

            # for sorting by the nth list in a zip, you input argument... key=lambda x: x[n])
            false_history = history.reindex(columns=percent_sorted)
            false_history = false_history[false_history.columns[::-1]]

    if len(history) > MOMENTUM_PERIOD:

        # buy logic
        if not in_position:
            # we do this so that next time around it will create a new row.
            new_row = True
            print(false_history.tail(MOMENTUM_PERIOD))

            # make sure the top coin is accelerating, if not look at the next highest coin
            for col, price in enumerate(false_history.iloc[-1, :]):

                top_coin = false_history.iat[0, col]
                top_coin_change = percent_change(false_history.iat[len(false_history) - 1, col], false_history.iat[len(false_history) - 2, col])
                latest_changes = [false_history.iat[-MOMENTUM_PERIOD + i, col] for i in range(0, MOMENTUM_PERIOD)]
                top_coin_mov = moving_average(latest_changes, MOMENTUM_PERIOD)

                # if there is acceleration and that coin is not bitcoin
                if top_coin_change >= top_coin_mov >= 0:
                    do_not_check = ['BTCUSD', 'XRPUSD', 'DAIUSD']
                    if top_coin not in do_not_check:
                        top_coin_price = false_history.iat[len(false_history) - 1, col]
                        buy_column = false_history.columns[col]
                        break

            # give me the details of the coin I'm looking at buying
            coin_info = client.get_symbol_info(top_coin)
            coin_filter_info = coin_info['filters']
            lot_size_info = dict(coin_filter_info[2])
            min_step = float(lot_size_info.get('stepSize'))

            buy_amount = round((betting_money / top_coin_price), 7)
            buy_coin = top_coin

            # if the min_step is higher than my buy precision, order won't go through, so we round it.
            if len(str(min_step)) < len(str(buy_amount)):
                sig_figs = len(str(min_step))
                if buy_coin == 'DOGEUSD':
                    buy_amount = round(buy_amount, sig_figs - 3)
                elif buy_amount == 'BTCUSD':
                    buy_amount = buy_amount
                else:
                    buy_amount = round(buy_amount, sig_figs - 2)

            # fake sell logic
            if not real_trading:
                # your buy amounts are off
                print(f'paid {round(top_coin_price*buy_amount, 2)} for {buy_amount} of {buy_coin} at price of {top_coin_price}', '\n')

            # actual binance buy
            if real_trading:
                buy_succeeded = order(SIDE_BUY, buy_amount, symbol=f'{buy_coin}')
                fills = my_order.get('fills')
                fills = dict(fills[0])
                price = fills.get('price')
                symbol = my_order.get('symbol')
                money = float(my_order.get('cummulativeQuoteQty'))
                quantity = float(my_order.get('executedQty'))

                print(f'wanted to pay {round(top_coin_price*buy_amount, 2)}')
                print(f"order info: paid {money} for {quantity} of {symbol} at a price of {price}")

            in_position = True
            return



        # sell logic
        if in_position:
            # find column that I have bought and get details:
            latest_change = percent_change(history.iat[-2, buy_column], history.iat[-1, buy_column])
            latest_changes = [history.iat[-MOMENTUM_PERIOD + i, buy_column] for i in range(0, MOMENTUM_PERIOD)]
            latest_mov = moving_average(latest_changes, MOMENTUM_PERIOD)

            if latest_mov < sell_percent:

                # new_row is set to false, so that we don't make a new row of the history df.
                new_row = False
                in_position = False

                # fake trading sell
                if not real_trading:
                    print(f'{buy_coin} went down {latest_change}%')
                    sell_price = history.iat[-1, buy_column]
                    sell_amount = round(sell_price*buy_amount*commission_multiplier, 3)

                    print(f"order info: sold {buy_amount} of {buy_coin} at a price of {sell_price} for {sell_amount}")
                    print(f'betting money is now {sell_amount}', '\n')

                    # recursive step with the sell amount
                    shaka(sell_amount, sell_perc)
                    return

                # actual binance sell
                if real_trading:
                    sell_price = history.iat[-1, buy_column]

                    sell_succeeded = order(SIDE_SELL, buy_amount, symbol=f'{buy_coin}')
                    fills = my_order.get('fills')
                    fills = dict(fills[0])
                    price = fills.get('price')
                    symbol = my_order.get('symbol')
                    money = float(my_order.get('cummulativeQuoteQty'))
                    quantity = float(my_order.get('executedQty'))

                    print(f'wanted to sell at {sell_price}')
                    print(f"order info: sold {quantity} of {symbol} at a price of {price} for {money}")
                    print(f'betting money is now {money}')

                    # recursive step with the money output from the trade
                    shaka(money, sell_perc)
                    return

            print(f'In position, {latest_change} >= {sell_percent}, price is {history.iat[-1, buy_column]}',  '\n')
            return


while True:
    shaka(starting_money, sell_perc)
    time.sleep(wait_minutes)
"""