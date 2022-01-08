from os import major
import numpy as np
from numpy.core.numeric import roll
from numpy.lib.function_base import piecewise
import pandas as pd
from macro_trendinator import trendinator
from cheap_algos import *
from candle_patterns import *

def get_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        # naughty timezone I'll have to deal with later.
        dates = df["Local time"].str[:-16]
        dates = pd.to_datetime(dates)
        df.drop(['Local time'], axis=1, inplace=True)
        df["Date"] = dates
        
        return df
    except:
        NameError
        "cannot find file."


def all_majors():
    major_ls = ['AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']
    df = pd.DataFrame()
    for pair in major_ls:
        x = get_data(f"FXMajors/{pair}.csv")
        df[f"{pair}"] = x["Close"]
    df["Date"] = x["Date"]
    return df

def sma_strategy(series, short_ma, long_ma):
    sell_pc = 0
    pc_changes=[]
    
    # this is just to get the data to daily format from 4h and to initialize my Moving averages
    series = [j for (i,j) in enumerate(series) if i % 6 == 0]
    short_avs = [0]*long_ma
    long_avs = [0]*long_ma

    for i,j in enumerate(series):
        # do not start calc until short and long ma's can be evaluated... 
        if i >= long_ma:
            short = np.average(series[i-short_ma:i])
            long = np.average(series[i-long_ma:i])
            short_avs.append(short)
            long_avs.append(long)
    
    df = pd.DataFrame()
    df['Close'] = series
    df["Short"] = short_avs
    df["Long"] = long_avs
    #df["Short Diff"] = df["Short"].diff()
    #df["Long Diff"] = df["Long"].diff()
    df.fillna(0, inplace=True)

    bought = False

    # buy and sell conditions
    for ind, val in enumerate(df["Short"].values):
        # buy if short_ma > long_ma
        if bought == False and val > df.iloc[ind, -1]:
            buy_ind, buy_val = ind, df.iloc[ind, 0]
            bought = True
            continue
        
        x = 90
        # sell if short_ma reverses.
        if bought == True and ind < len(series) - x:
            if ind == buy_ind+x:
                trade_pc = percent_change(buy_val, df.iloc[ind+5, 0])
                pc_changes.append(trade_pc)
                bought = False
        

    if bought == True:
        final_trade = percent_change(buy_val, df.iloc[-1, 0])
        pc_changes.append(final_trade)
    
    avg = round(np.average(pc_changes), 3)
    wins = round(len([i for i in pc_changes if i > 0]) / len(pc_changes), 2)
    std = round(np.std(pc_changes), 3)


    return (avg, wins, std, len(pc_changes))


def bb_strategy(series, ma_period=20):
    pc_changes=[]
    
    # this is just to get the data to daily format from 4h and to initialize my Moving averages
    series = [j for (i,j) in enumerate(series) if i % 6 == 0]
    moving_averages, upperBB, lowerBB = [[0]*ma_period for _ in range(3)]


    for i,j in enumerate(series):
        # do not start calc until short and long ma's can be evaluated... 
        if i >= ma_period:
            ma = BBands(series[i-ma_period:i])
            upperBB.append(ma[0])
            moving_averages.append(ma[1])
            lowerBB.append(ma[2])
    
    df = pd.DataFrame()
    df['Close'] = series
    df["UpperBB"], df["MA"], df["LowerBB"] = upperBB, moving_averages, lowerBB
    df.fillna(0, inplace=True)
    df.round(5)
    bought = False

    # df is in col format [close, upper, ma, lower]
    # Now on to the buy and sell conditions
    for ind, val in enumerate(df["Close"].values):
        # buy if price dips below lowerBB
        if bought == False and val < df.iloc[ind, -1]:
            buy_val = df.iloc[ind, 0]
            bought = True
            continue
        
        # sell if price dips above upperBB
        if bought == True and val > df.iloc[ind, 1]:
            trade_pc = percent_change(buy_val, df.iloc[ind, 0])
            pc_changes.append(trade_pc)
            bought = False
        

    if bought == True:
        final_trade = percent_change(buy_val, df.iloc[-1, 0])
        pc_changes.append(final_trade)
    
    avg = round(np.average(pc_changes), 3)
    wins = round(len([i for i in pc_changes if i > 0]) / len(pc_changes), 2)
    std = round(np.std(pc_changes), 3)


    return (avg, wins, std, len(pc_changes))


def candle_strategy(df):
    pc_changes, trade_lengths, my_ls  = [], [], []
    bought = False
    sold = False

    # first we must get a moving avg col for our df
    moving_averages = [0]*3
    pc_or_no = [0]*9




    closes = df["Close"].values
    pc_from_start = [percent_change(closes[0], closes[ind]) for ind in range(0, len(df))]
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
            check_window = df.iloc[ind-2:ind+1, 0:4]
            # check for the 4 downtrend reversal patterns.
            downtrend_candle_patterns = [three_white_soldiers, three_inside_up, three_outside_up, morning_star]
            pc_or_no.append(0)

            for pattern in downtrend_candle_patterns:
                x = pattern(check_window)
                if x:
                    # print(check_window)
                    # print(f"'{pattern.__name__}' detected")
                    buy_ind, buy_val = ind, df.iloc[ind,3]
                    bought = True
                    break
            continue
        
        if bought == True and uptrend:
            # check for the 4 uptrend reversal patterns
            check_window = df.iloc[ind-2:ind+1, 0:4]
            uptrend_candle_patterns = [three_black_crows, three_inside_down, three_outside_down, evening_star]

            for pattern in uptrend_candle_patterns:
                x = pattern(check_window)
                if x:
                    # print(check_window)
                    # print(f"'{pattern.__name__}' detected")
                    
                    # sell at open of next candle
                    trade_pc = percent_change(buy_val, df.iloc[ind, 0])
                    trade_len = ind - buy_ind
                    my_ls.append([buy_ind, buy_val, ind, df.iloc[ind, 0]])
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
    
    avg_trade_len = np.average(trade_lengths)
    avg = round(np.average(pc_changes), 3)
    wins = round(len([i for i in pc_changes if i > 0]) / len(pc_changes), 2)
    std = round(np.std(pc_changes), 3)


    return (avg, wins, std, len(pc_changes), round(avg_trade_len), my_ls, pc_or_no, pc_from_start)


def clean():
    fx_ls = ["AUDCAD", "AUDNZD", "CADCHF", "CADHKD", "CHFJPY", "CHFSGD", "EURAUD", "EURCAD", "EURCHF", "EURPLN", "EURSEK", "EURTRY", "HKDJPY", "ZARJPY", "USDZAR", "USDTRY", "USDTHB", "USDNOK", "USDMXN", "USDHUF"]
    major_ls = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    fx_ls.extend(major_ls)
    # fucking EURRUB doesn't go back that far, so he got cut.
    fx = pd.DataFrame()
    for pair in fx_ls:
        df = pd.read_csv(f'FX/{pair}_4h.csv')

        df = get_data(f"FX/{pair}_4h.csv")
        df.drop_duplicates(subset=["Open", "High", "Low", "Close"], keep=False, inplace=True)
        values = df['Close'].values
        values = values[:7350]
        #fx[f'{pair}'] = values
    
        mov = [0]*2
        for i,j in enumerate(values):
            # The file's index starts at 1!!!!!!!!!! 
            if i >= 2:
                ma = np.average(values[i-2:i+1])
                mov.append(ma)
        fx[f"{pair}"] = mov
    print(fx)    
    #fx.to_csv('Backtesting/mov_4h.csv', index=False)
    


#p = clean()


def backtest_all():
    
    major_ls = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    avgs, wins, stds, trades = [[] for _ in range(4)]
    rolling_pcs = pd.DataFrame()
    real_pcs = pd.DataFrame()

    first = True
    for pair in major_ls:
        df = get_data(f"FXMajors/{pair}_4h.csv")
        df.drop_duplicates(subset=["Open", "High", "Low", "Close"], keep=False, inplace=True)
 
        x = candle_strategy(df)
        avgs.append(x[0])
        wins.append(x[1])
        stds.append(x[2])
        trades.append(x[3])

        # the following is simply to handle varying lengths of output lsts
        start = int(len(x[6])*0)
        fin = int(len(x[6])*0.90)
        len_x6, len_x7 = x[6], x[7]
        len_x6, len_x7 = len_x6[start:fin], len_x6[start:fin]

        if first:
            length_first = len(len_x6)
            first = False
        if len(len_x6) > length_first:
            len_x6, len_x7 = len_x6[:-1], len_x7[:-1]
        rolling_pcs[f"{pair}"] = len_x6
        real_pcs[f"{pair}"] = len_x7




    win = np.average(wins)


    #print(f"BB strategy, ma_period at {ma_period}")
    print(f"Avg win {round(np.average(avgs), 3)}, {sum(trades)} trades,  wins {round(win*100, 1)}% time, std = {round(np.average(stds), 3)}")
    print('--------------------')

    return (rolling_pcs, real_pcs)


#x = backtest_all()
#print(x[1])

def backtest(file):
    df = pd.read_csv(file, usecols=["Open", "High", 'Low', "Close"])
    x = candle_strategy(df)
    return (x, x[5])

#x = backtest("historical_data/spy_hourly.csv")
# print(x)


def fx_candle_realism(max_threads, max_holding_time):
    """
    Pass in dfs of opens, closes, avgs
    """
    closes = pd.read_csv('Backtesting/closes_4h.csv')
    opens = pd.read_csv('Backtesting/opens_4h.csv')
    moving_averages = pd.read_csv('Backtesting/mov_4h.csv')

    df = pd.concat([opens, closes, moving_averages], axis=1)
    #df = df[:2000]
    current_positions = 0
    bought, trade_pcs, c, holding_time, trade_info, pattern_array  = [[] for _ in range(0,6)]

    # iterate by row through the df
    for ind, row in df.iterrows():
        if ind > 10:
            c.append(current_positions)
            for col in range(0,len(closes.columns)):
                window = df.iloc[ind-7:ind+1,col::len(closes.columns)]
                MAs = window.iloc[:-1, 1]
                my_col = window.columns[0]
                t = trend_finder(MAs.values, 5)
                b = [i for i,j,k in bought]


                # SELL CONDITIONS
                if my_col in b:
                    my_buy = [(i,j,k) for i,j,k in bought if i == my_col]
                    uptrend_candle_patterns = [three_black_crows, three_inside_down, three_outside_down, evening_star]
                    little_window = window.iloc[-3:, :]
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
                                pattern_array.append(pattern.__name__)

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
                                pattern_array.append(pattern.__name__)

                                buy_info = (window.columns[0], window.iloc[-1,1], ind)
                                bought.append(buy_info)
                                current_positions += 1
                                break
    
    
    # gimme how many times each candle pattern appeared:
    for p in uptrend_candle_patterns + downtrend_candle_patterns:
        p = p.__name__
        uses = pattern_array.count(p)
        print(f'{p} used {uses} times')


    avg = np.average(trade_pcs) / max_threads
    std = np.std(trade_pcs) / max_threads
    avg_pos_count = np.average(c)
    avg_ht = np.average(holding_time)
    avg_ht = avg_ht / 6
    avg_per_wk = (avg / avg_ht)*7
    ls = [avg, len(trade_pcs), avg_pos_count, avg_per_wk]
    ls = [round(i*50, 3) for i in ls]
    ls[1] = len(trade_pcs)
    ls[2] = round(avg_pos_count, 2)
    ls.append(round(np.average(holding_time), 2))

    # trade_info has all the (pc, ind) for graphs
    the_goods = []
    for ind in range(0, len(df[10:])):
        if ind in [j for i,j in trade_info]:
            the_goods.append([i for i,j in trade_info if j == ind][0])
        else:
            the_goods.append(0)


    return ls


x = fx_candle_realism(10, 200)
print(x)
