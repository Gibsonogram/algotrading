import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cheap_algos import percent_change
pd.options.mode.chained_assignment = None

# params
RSI_sell = 46
RSI_buy = 34
autosell = 18
delay = 1


opens = pd.read_csv('Binance/opens_4h.csv', usecols=range(50))
closes = pd.read_csv('Binance/closes_4h.csv', usecols=range(50))
opens, closes = opens[:2500], closes[:2500]

def RSIcalc(asset_df, RSI_buy = RSI_buy):
    """
    Params
    """
    df = pd.DataFrame()
    df['Open'] = asset_df['Open']
    df['Close'] = asset_df['Close']
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Price Change'] = df['Close'].pct_change()
    df['Upmove'] = df['Price Change'].apply(lambda x: x if x > 0 else 0)
    df['Downmove'] = df['Price Change'].apply(lambda x: abs(x) if x < 0 else 0)
    
    # this fucking ES fxn means we have to do a bunch of calculations to get accurate difference for RS
    df['Avg Up'] = df['Upmove'].ewm(span=19).mean()
    df['Avg Down'] = df['Downmove'].ewm(span=19).mean()
    df = df.dropna(0)
    
    df['RS'] = df['Avg Up'] / df['Avg Down']
    df['RSI'] = df['RS'].apply(lambda x: 100 - (100 / (x+1)))

    # buy condition
    df.loc[(df['Close'] >= df['MA200']) & (df['RSI'] < RSI_buy), 'Buy'] = 'Yes'
    df.loc[(df['Close'] < df['MA200']) | (df['RSI'] >= RSI_buy), 'Buy'] = 'No'

    return df
    

def get_signals_backtesting(df, RSI_sell = RSI_sell, tts=autosell):
    buying_inds, selling_inds = [],[]

    for i in range(len(df)-tts):
        if 'Yes' in df['Buy'].iloc[i]:
            buying_inds.append(df.iloc[i+1].name)
            for j in range(1,tts+1):
                if df['RSI'].iloc[i + j] > RSI_sell:
                    selling_inds.append(df.iloc[i+j+1].name)
                    #trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])
                    break
                elif j == tts:
                    selling_inds.append(df.iloc[i+j+1].name)
                    #trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])

    return buying_inds, selling_inds


def get_signals(df, RSI_sell = RSI_sell, tts=autosell):
    buying_inds, selling_inds = [],[]

    for i in range(len(df)-tts-delay):
        if 'Yes' in df['Buy'].iloc[i]:
            buying_inds.append(df.iloc[i+delay].name)
            for j in range(1,tts+1):
                if df['RSI'].iloc[i + j] > RSI_sell:
                    selling_inds.append(df.iloc[i+j+delay].name)
                    #trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])
                    break
                elif j == tts:
                    selling_inds.append(df.iloc[i+j+delay].name)
                    #trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])

    return buying_inds, selling_inds





def RSI_backtesting():
    for f in range(24,25):
        
        profit_arr, prof_pc, trade_num, avg_trade_len = [[] for _ in range(4)]
        for col in closes.columns:
            frame = RSIcalc(closes[col])
            buy, sell, trade_lens = get_signals_backtesting(frame, tts=f)
            if len(trade_lens) < 2:
                continue
            p = (frame.loc[sell]['Open'].values - frame.loc[buy]['Open'].values) / frame.loc[buy]['Open'].values
            profit_arr.append(np.average(p))
            prof_pc.append(len([i for i in p if i > 0]) / len(p))
            trade_num.append(len(p))
            avg_trade_len.append(np.average(trade_lens))
        
        overall = np.average(profit_arr)*100 # for percent
        win_rate = np.average(prof_pc)
        t = np.average(avg_trade_len)
        ls = [round(i, 3) for i in [overall, win_rate, t]]
        ls.append(sum(trade_num))
        print(ls, f'tts (autosell) = {round(f / 6, 2)} days')
        print('------------------')
    
    return



def RSI_strategy(max_threads, tts):
    """
    Params
    ______________
    max_threads: max # of positions that can be open
    tts: time to autosell.

    """
    # just get the results of the RSI calcs for each df
    bs = []
    for col in closes.columns:
        x = pd.DataFrame()
        x['Open'] = opens[col]
        x['Close'] = closes[col]
        frame = RSIcalc(x)
        buy, sell = get_signals(frame, tts=tts)
        bs.append((buy, sell))
    
    bought, profits, apc, gimme_some_sugar = [[] for _ in range(4)]
    current_positions = 0

    # part 2
    for ind in range(len(closes)):
        if ind > 200:
            sells_this_row = []
            apc.append(current_positions)
            for col, tuple in enumerate(bs):
                buys = tuple[0]
                sells = tuple[1]
                
                # bought[0] is col#
                sells_to_check = [i for i,j,k in bought]
                if col in sells_to_check:
                    # check for sell
                    if ind in sells:

                        to_remove = [(i,j,k) for i,j,k in bought if i == col][0]
                        sell_value = opens.iloc[ind, col]
                        pc = percent_change(to_remove[1], sell_value)
                        # for fees
                        pc = pc*0.99925
                        profits.append(pc)

                        bought.remove(to_remove)
                        current_positions -= 1
                        sells_this_row.append(pc)
                
                # buys
                if buys and current_positions < max_threads:
                    if ind in buys:
                        already_bought = [i for i,j,k in bought]
                        if col not in already_bought:
                            buy_value = opens.iloc[ind, col]
                            bought.append((col, buy_value, closes.columns[col]))
                            current_positions += 1
            
            if sells_this_row:
                gimme_some_sugar.append(sum([i for i in sells_this_row]) / max_threads)
            else:
                gimme_some_sugar.append(0)
    
    print(f'{len(profits)} trades')
    oft = len([i for i in apc if i != 0]) / len(apc) * 100
    win_rate = len([i for i in profits if i > 0]) / len(profits) * 100
    profits = np.average(profits)
    apc = np.average(apc)
    ls = [round(i, 3) for i in [profits, win_rate, apc, oft]]
    print('Avg Profit, Win rate, Threads being used, % time in trades')

    return ls, gimme_some_sugar




# graphing

res, x = RSI_strategy(3, autosell)
print(res)
running_pc, profit = 0, []


for i in x:
    running_pc += i
    profit.append(running_pc)

plt.figure(figsize=(12,5))
plt.plot(profit)
plt.show()


