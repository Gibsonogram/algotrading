from operator import index
from typing import final
from numpy.core.fromnumeric import shape
import pandas as pd
#from binance_functions import *
from cheap_algos import *
from candle_patterns import *


opens = pd.read_csv('Binance/opens_4h.csv', usecols=range(0,50))
closes = pd.read_csv('Binance/closes_4h.csv', usecols=range(0,50))
#opens, closes = opens[3000:], closes[3000:]





def make_MAs():
    df = pd.DataFrame()
    for col in closes.columns:
        values = closes[f'{col}'].values
        mov = [0]*3
        for i,j in enumerate(values):
            # do not start calc until short and long ma's can be evaluated... 
            if i > 2:
                ma = np.average(values[i-2:i+1])
                mov.append(ma)
        df[f"{col}"] = mov
    df = df.round(8)
    return df

"""
...

Step 2) Adapt fxn to also work with Forex backtesting info

Step 3) Avg those MF's together to get avg profit.
"""


def candle_strategy_realism(max_threads, max_holding_time):
    """
    Pass in dfs of opens, closes, avgs

    """
    col_count = 50
    opens = pd.read_csv('Binance/opens_4h.csv', usecols=range(0,col_count))
    closes = pd.read_csv('Binance/closes_4h.csv', usecols=range(0,col_count)) 
    moving_averages = pd.read_csv('Binance/moving_averages_4h.csv', usecols=range(0,col_count))
    df = pd.concat([opens, closes, moving_averages], axis=1)
    current_positions = 0


    bought, trade_pcs, c, holding_time, trade_info  = [[] for _ in range(0,5)]

    # iterate by row through the df
    for ind, row in df.iterrows():
        if ind > 10:
            c.append(current_positions)
            for col in range(0,col_count):
                window = df.iloc[ind-6:ind+1,col::col_count]
                cl = window.iloc[:, 1]
                my_col = window.columns[0]
                t = trend_finder(cl.values)
                b = [i for i,j,k in bought]


                # SELL CONDITIONS
                if my_col in b:
                    my_buy = [(i,j,k) for i,j,k in bought if i == my_col]
                    uptrend_candle_patterns = [three_black_crows, three_inside_down, three_outside_down, evening_star]
                    little_window = window.iloc[-3:,:]
                    little_window.columns = ['Open', 'Close', 'MA']
                    
                    if ind - my_buy[0][2] > max_holding_time:

                        holding_time.append(max_holding_time)
                        pc = percent_change(float(my_buy[0][1]), float(little_window.iloc[-1,1]))
                        trade_pcs.append(pc)

                        bought.remove(my_buy[0])
                        current_positions -= 1
                        trade_info.append((pc / max_threads, ind))
                        break

                    if t == 'uptrend':
                        for pattern in uptrend_candle_patterns:
                            x = pattern(little_window)
                            if x:
                                # print(check_window)
                                # print(f"'{pattern.__name__}' detected")
                                pc = percent_change(float(my_buy[0][1]), float(little_window.iloc[-1,1]))
                                trade_pcs.append(pc)
                                holding_time.append(ind - my_buy[0][2])
                                trade_info.append((pc / max_threads, ind))

                                bought.remove(my_buy[0])
                                current_positions -= 1
                                break


                # BUY CONDITION
                if my_col not in b and current_positions < max_threads:
                    if t == 'downtrend':
                        downtrend_candle_patterns = [three_white_soldiers, three_inside_up, three_outside_up, morning_star]
                        little_window = window.iloc[-3:,:]
                        little_window.columns = ['Open', 'Close', 'MA']
                        for pattern in downtrend_candle_patterns:
                            x = pattern(little_window)
                            if x:
                                # print(check_window)
                                # print(f"'{pattern.__name__}' detected")
                                buy_info = (window.columns[0], window.iloc[-1,1], ind)
                                bought.append(buy_info)
                                current_positions += 1
                                break
    
    avg = np.average(trade_pcs) / max_threads
    std = np.std(trade_pcs) / max_threads
    avg_pos_count = np.average(c)
    avg_ht = np.average(holding_time)
    avg_ht = avg_ht / 6
    avg_per_wk = (avg / avg_ht)*7
    ls = [avg, std, len(trade_pcs), avg_pos_count, avg_per_wk]
    ls = [round(i, 3) for i in ls] 

    # trade_info has all the (pc, ind) for graphs
    the_goods = []
    for ind in range(0, len(df[10:])):
        if ind in [j for i,j in trade_info]:
            the_goods.append([i for i,j in trade_info if j == ind][0])
        else:
            the_goods.append(0)


    return the_goods


#x = candle_strategy_realism(2, 100)
#print(x)







def candle_strategy_backtesting(df):
    pc_changes, trade_lengths, my_ls  = [], [], []
    bought = False
    sold = False

    # first we must get a moving avg col for our df
    moving_averages = [0]*3
    pc_or_no = [0]*9

    closes = df["Close"].values
    
    for i,j in enumerate(closes):
        # do not start calc until short and long ma's can be evaluated... 
        if i > 2:
            ma = np.average(closes[i-2:i+1])
            moving_averages.append(ma)
    df["MA"] = moving_averages
    df = df.round(5)
    # now we can do our candlestick business
    for ind in range(9, len(df)):
        # first we check for the trend:
        # the value of the trend that will actually be used is moving avg at t-2. 
        uptrend, downtrend = False, False
        up, down = 0,0
        ma_values = moving_averages[ind - 7:ind-1]
        for i,j,k in zip(ma_values, sorted(ma_values), reversed(sorted(ma_values))):
            if up > 4:
                uptrend = True
                break
            if down > 4:
                downtrend = True
                break
            if i == j:
                up += 1
            if i == k:
                down += 1


        # check for each candlestick pattern
        if bought == False and downtrend:
            check_window = df.iloc[ind-2:ind+1, :]
            # check for the 4 downtrend reversal patterns.
            downtrend_candle_patterns = [three_white_soldiers, three_inside_up, three_outside_up, morning_star]
            pc_or_no.append(0)

            for pattern in downtrend_candle_patterns:
                x = pattern(check_window)
                if x:
                    # print(check_window)
                    # print(f"'{pattern.__name__}' detected")
                    buy_ind, buy_val = ind, df.iloc[ind, 0]
                    bought = True
                    break
            continue
        
        if bought == True:
            if uptrend:
                # check for the 4 uptrend reversal patterns
                check_window = df.iloc[ind-2:ind+1,:]
                uptrend_candle_patterns = [three_black_crows, three_inside_down, three_outside_down, evening_star]

                for pattern in uptrend_candle_patterns:
                    x = pattern(check_window)
                    if x:
                        # print(check_window)
                        # print(f"'{pattern.__name__}' detected")
                        
                        # sell at open of next candle
                        trade_pc = percent_change(buy_val, df.iloc[ind, 0])
                        trade_len = ind - buy_ind
                        #my_ls.append([buy_ind, buy_val, ind, df.iloc[ind, 0]])
                        trade_lengths.append(trade_len)
                        pc_changes.append(trade_pc)
                        sold = True

                        bought = False
                        break
        
        if sold:
            pc_or_no.append(trade_pc)
            sold = False
        else:
            pc_or_no.append(0)

    if bought == True:
        final_trade = percent_change(buy_val, df.iloc[-1, 0])
        pc_changes.append(final_trade)
    
    # relegating all results and returning
    if len(pc_changes) > 1:
        ls = [pc_changes, trade_lengths]
        res = [np.average(i) for i in ls]
        win_pc = len([i for i in pc_changes if i > 0])*100 / len(pc_changes)
        std = np.std(pc_changes)
        res.extend([win_pc, std, len(pc_changes)])
        res = [round(i,2) for i in res[:-1]]
        res.append(pc_or_no)

        # returns [avg_pc, avg_trade_len, win_pc, std, total_trades, pc_or_no -> list]  
        return res
    else:
        return 'no trades'


def backtest():
    avie, trade_len, win_rate, stds  = [[] for _ in range(0,4)]
    ls = [avie, trade_len, win_rate, stds]
    pc_df = pd.DataFrame()
    
    for col in opens.columns:
        df = pd.DataFrame()
        df['Open'] = opens[col].values
        df['Close'] = closes[col].values
        x = candle_strategy_backtesting(df)
        if x == 'no trades':
            continue
        else:
            pc_df[f'{col}'] = x[-1]
            do = [j.append(x[i]) for i,j in enumerate(ls)]

    total_trades = round(sum(ls[-1]))
    res = [round(np.average(i), 2) for i in ls[:-1]]
    res.append(total_trades)
    pc_df['sum'] = pc_df.sum(axis=1)
    
    return pc_df

#x = backtest() ; print(x)



def candle_strategy(df, bought):
    # firstly, this fxn only needs to check certain things, depending on whether we are holding the coin or not.
    # the following chunk gets an MA col for our df.
    moving_averages = [0]*2
    coin_closes = df.columns[0]
    closes = df[coin_closes].values
    
    for i,j in enumerate(closes):
        if i > 1:
            ma = np.average(closes[i-2:i+1])
            moving_averages.append(ma)
    
    dfw = df.copy()
    dfw["MA"] = moving_averages
    df = dfw.round(5)

    # first we check for the trend:
    # the value of the trend that will actually be used is moving avg at ind-2.
    uptrend, downtrend = False, False
    up, down = 0,0
    ma_values = moving_averages[-8:-2]
    for i,j,k in zip(ma_values, sorted(ma_values), reversed(sorted(ma_values))):
        if up > 4:
            uptrend = True
            break
        if down > 4:
            downtrend = True
            break
        if i == j:
            up += 1
        if i == k:
            down += 1
    
    
    # BUY CONDITIONS
    if not bought:
        if downtrend:
            check_window = df.iloc[-3:, :]
            check_window.columns = ['Open', 'Close', 'MA']
            # check for the 4 downtrend reversal patterns.
            downtrend_candle_patterns = [three_white_soldiers, three_inside_up, three_outside_up, morning_star]

            for pattern in downtrend_candle_patterns:
                # candle patterns return True or False
                x = pattern(check_window)
                if x:
                    # print(f"'{pattern.__name__}' detected")
                    return 'buy'
        return 'leave'
    
    # SELL CONDITIONS
    if bought:
        if uptrend:
            # check for the 4 uptrend reversal patterns
            check_window = df.iloc[-3:,:]
            check_window.columns = ['Open', 'Close', 'MA']
            uptrend_candle_patterns = [three_black_crows, three_inside_down, three_outside_down, evening_star]

            for pattern in uptrend_candle_patterns:
                x = pattern(check_window)
                if x:
                    # print(check_window)
                    # print(f"'{pattern.__name__}' detected")
                    return 'sell'
        return 'hold'
    

    # returns 'buy', 'leave', 'sell' or 'hold'
