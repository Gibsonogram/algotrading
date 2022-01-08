import pandas as pd
from rsi_strategy import RSIcalc
from binance_functions import *
from cheap_algos import *
import config
from binance.enums import *
import binance.client
from datetime import datetime, timedelta
import time
from math import log10

Client = binance.client.Client
wait_minutes = 1
starting_money = 10

# this gets the keys from config.py file which is .gitignored for my safety.
# we make the timeout time 30 seconds instead of default 10. This allows it to actually complete orders consistently
client = Client(config.API_KEY, config.API_SECRET, tld='us', requests_params={'timeout': 30})


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        my_order = client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type)
        return my_order
    except:
        return 'order failed'


def get_min_step(coin):
    """
    Gets the minimum step size for coin/pair on binance.
    This is important because if you do not round off, your binance order will not go through.
    returns the number you will need to round off to.
    """
    coin_info = client.get_symbol_info(f'{coin}')
    coin_filter_info = coin_info['filters']
    lot_size_info = dict(coin_filter_info[2])
    min_step = lot_size_info.get('stepSize')
    
    # Yes I do feel clever about the next line.
    # No I didn't think of it immediately.
    return int(abs(log10(float(min_step))))


def account_details():
    """
    This absurdly large fxn just gets all the info I want to keep track of from binance account.
    Returns: ls object of form: 
    [current_usd, overall_balance, # of open positions of value > $1, array of open positions of form ('coin', amount)]
    Ex:
    [100.00, 136.00, [('BAND', 6.00), ('SHIB', 30.00)]]
    """
    x = client.get_account()
    
    # wrangling this annoying json format into useable info
    x =list(x.items())
    balances = x[9][1]
    balances = [list(b.values()) for b in balances]
    balances = [(i,j) for (i,j,k) in balances]
    holding = [(i,j) for (i,j) in balances if float(j) > 0]
    usd_amount = float(holding.pop(1)[1])
    
    stables = ['USDT', 'BUSD', 'BNB', 'DAI', 'USDC']
    holding = [(i,j) for (i,j) in holding if i not in stables]

    current_prices = client.get_symbol_ticker()
    current_prices = [list(i.items()) for i in current_prices]
    current_prices = [(i[1][:-3], j[1]) for (i,j) in current_prices if i[1][-3:] == 'USD']
    current_prices = [(i,j) for (i,j) in current_prices if i in [i for i,j in holding]]
    actual = []
    for i,j in current_prices:
        for k, l in holding:
            if i == k:
                actual.append([i, float(j)*float(l), l])
                # actual has the form [coin, usd amount, coin amount]

    overall_balance = sum([float(j) for i,j,k in actual])+usd_amount
    real_positions = [(i,j,k) for i,j,k in actual if j > (overall_balance / 100)]

    res = [usd_amount, overall_balance, real_positions]
    return res


def shaka(max_threads=3, RSI_buy = 34, RSI_sell = 46):
    # get dat data
    # for RSI strategy we need at least 200 periods, so 34 days
    start_time = datetime.today() - timedelta(days=34)
    str_start_time = str(start_time)[:-10] # -> bc binance is dumb and wants str instead of datetime...
    candle_data = all_coin_data('4h', str_start_time)
    acc = account_details()
    overall = round(acc[1], 2)
    current_positions = acc[2]
    pos_count = len(acc[2])
    coins = [str(i)[:-5] for i in candle_data.columns[:-1:2]]
    bought = [str(i)+'USD' for i,j,k in current_positions]

    rtrades = pd.read_csv('Binance/trade_history.csv')
    open_trades = rtrades[rtrades['Status'] == 'Open']
    
    sells, holds = [], []
    # SELL CONDITIONS
    for ind, row in open_trades.iterrows():
        coin = row.values[0]
        this_pos = [(i,j,k) for i,j,k in current_positions if str(i)+'USD' == coin][0]
        df = candle_data[[f'{coin}_Open', f'{coin}_Close']]
        df.columns = ['Open', 'Close']
        frame = RSIcalc(df)

        # check for sells based on time constraint
        if pd.to_datetime(row.values[1]) <= datetime.today() - timedelta(days=3):
            open_trades = open_trades.drop(row.name, axis=0)
            sells.append(this_pos)
            pos_count -= 1

        # check for sells based on RSI cond.
        elif frame.iloc[-1, -2] > RSI_sell:
            sells.append(this_pos)
            pos_count -= 1
        
        # else we must be holding it.
        else:
            holds.append(this_pos)
    
    # BUY CONDITIONS
    buys_to_check = [i for i in coins if i not in bought]
    buys = []
    for coin in buys_to_check:
        if pos_count < max_threads:
            df = candle_data[[f'{coin}_Open', f'{coin}_Close']]
            df.columns = ['Open', 'Close']
            frame = RSIcalc(df, RSI_buy=RSI_buy)
            if frame.iloc[-1,-1] == 'Yes':
                buys.append(coin)
                pos_count += 1
    
    capital = acc[0]
    return (capital, buys, sells, holds, overall)


def place_trades(max_threads, trading_percent = 0.10, sell_all_now=False):
    """
    Parameters
    ------------
    max_threads: hopefully we know what this means by now
    trading_percent (optional): float between [0,1] how much of your capital are you trading with.
    default is 0.50.
    sell_all_now (optional): Bool, just a nice option to exit all active trades, usually for maintenance.
    default is False
    """
    res = shaka(max_threads)
    # res will have the following form:
    # res = [500, ['ETHUSD', 'WAVESUSD'], [('BTCUSD', 10, 0.0002034), ('DOGEUSD', 200, 1205.5)], [('LTCUSD', 100, 0.44)], 740]
    capital = res[0] * trading_percent
    buy_coins = res[1]
    hold_coins = [str(i)+'USD' for i,j,k in res[3]]
    overall_balance = res[4]
    pos_count = len(res[2]) + len((res[3]))

    algo_status = pd.read_csv('Binance/algo_status.csv')
    trade_history = pd.read_csv('Binance/trade_history.csv')

    # grab the active trades
    open_trades = trade_history[trade_history['Status'] == 'Open']

    # SELL LOGIC
    # just a nice option to have
    if sell_all_now:
        sells = res[2]+res[3]
    else:
        sells = res[2]
    
    new_rows, sell_went_through = [], []
    for coin, usd_amount, coin_amount in sells:
        # if the min_step is higher than my buy precision, orders won't go through, so we round it.
        coin = str(coin)+'USD'
        min_step = get_min_step(coin)
        # DO THE SELL
        # subtract a small amount so that we do not round over how much we actually have...
        coin_amount = float(coin_amount)
        sell_amount = coin_amount - (coin_amount / 200)
        sell_amount = round(float(sell_amount), min_step)
        my_order = order(SIDE_SELL, sell_amount, symbol=f'{coin}')
        if my_order == 'order failed':
            print(f'wanted to sell {coin} but failed')
            continue
        else:
            fills = my_order.get('fills')
            fills = dict(fills[0])
            sell_price = fills.get('price')
            symbol = my_order.get('symbol')
            money = float(my_order.get('cummulativeQuoteQty'))
            pos_count -= 1
            capital += money
            sell_went_through.append(coin)

        # CATALOG SELLS
        csv_row = open_trades[open_trades['Coin'] == coin]
        new_row = csv_row.values.tolist()[0] # -> can't believe its this complicated to get row into a list format
        pc = percent_change(float(csv_row['Buy Price']), float(sell_price))
        new_row[3] = datetime.today().strftime('%Y-%m-%d %H:%m')
        new_row[4] = sell_price
        new_row[5] = 'Closed'
        new_row[6] = pc
        new_rows.append(new_row)
    
    # UPDATE TRADE HISTORY CSV
    # If list of sells is not empty,
    # drop the trades that were open, and append the new versions of them
    if sell_went_through:
        trades_just_closed = trade_history[trade_history['Status'] == 'Open'].index.tolist()
        trade_history.drop(trades_just_closed, axis=0, inplace=True)
        for row in new_rows:
            trade_history = trade_history.append(dict(zip(trade_history.columns, row)), ignore_index=True)
        trade_history = trade_history.reindex(range(0,len(trade_history)))

        # sleep for a few seconds to make sure sells go through and usd updates
        time.sleep(5)
    
    pcs = trade_history['Gain/Loss'].values
    average_pc = np.average([i for i in pcs if i != 0])
    


    # BUY LOGIC
    buy_went_through = []
    for coin in buy_coins:
        if pos_count < max_threads:
            min_step = get_min_step(coin)
            usd = capital / (max_threads - pos_count) # -> this ensures you buy the same fraction of your capital, regardless of how many threads are active. Yeah I feel clever about it.
            c = client.get_symbol_ticker()
            symbol = [i for i in c if i.get('symbol') == coin]
            current_price = float(symbol[0]['price'])
            buy_amount = round(usd / current_price, min_step)
            
            my_order = order(SIDE_BUY, buy_amount, symbol=f'{coin}')
            if my_order != 'order failed':
                fills = my_order.get('fills')
                fills = dict(fills[0])
                buy_price = fills.get('price')
                symbol = my_order.get('symbol')
                money = float(my_order.get('cummulativeQuoteQty'))

                buy_went_through.append(coin)
                pos_count += 1
                capital -= money       
            
                new_row = {
                    'Coin':coin,
                    'Buy Date':datetime.today().strftime('%Y-%m-%d %H:%m'),
                    'Buy Price': buy_price,
                    'Sell Date':'holding',
                    'Sell Price': buy_price,
                    'Status': 'Open',
                    'Gain/Loss': 0.0
                }
                trade_history = trade_history.append(new_row, ignore_index=True)
    
    current_status = {
        'Datetime': datetime.today().strftime('%Y-%m-%d %H:%m'),
        'Current Positions': pos_count,
        'Bought': buy_went_through,
        'Sold': sell_went_through,
        'Holding': hold_coins,
        'Avg Percent': average_pc,
        'Trading Balance': round(overall_balance, 2)
    }
    algo_status = algo_status.append(current_status, ignore_index=True)
    algo_status.fillna(0, inplace=True)
    print(algo_status)

    
    
    algo_status.to_csv('Binance/algo_status.csv', index=False)
    trade_history.to_csv('Binance/trade_history.csv', index=False)




# DANGER ZONE

#place_trades(3)

while True:
    place_trades(3, 0.05)
    time.sleep(60*240)




