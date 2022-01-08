import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None


opens = pd.read_csv('Backtesting/opens_4h.csv')
closes = pd.read_csv('Backtesting/closes_4h.csv')

df = pd.concat([opens, closes], axis=1)

def RSIcalc(asset, col='AUDUSD'):
    """
    Will be fed a df col.
    """
    df = pd.DataFrame()
    df['Close'] = asset
    df['Open'] = opens[col]
    df['MA200'] = df['Close'].rolling(window=200).mean()
    df['Price Change'] = df['Close'].pct_change()
    df['Upmove'] = df['Price Change'].apply(lambda x: x if x > 0 else 0)
    df['Downmove'] = df['Price Change'].apply(lambda x: abs(x) if x < 0 else 0)
    df['Avg Up'] = df['Upmove'].ewm(span=19).mean()
    df['Avg Down'] = df['Downmove'].ewm(span=19).mean()
    df = df.dropna(0)

    df['RS'] = df['Avg Up'] / df['Avg Down']
    df['RSI'] = df['RS'].apply(lambda x: 100 - (100 / (x+1)))

    # buy condition
    df.loc[(df['Close'] >= df['MA200']) & (df['RSI'] < 30), 'Buy'] = 'Yes'
    df.loc[(df['Close'] < df['MA200']) | (df['RSI'] >= 30), 'Buy'] = 'No'
    
    return df

def get_signals(df, tts=10):
    buying_inds, selling_inds, trade_len = [],[],[]

    for i in range(len(df)-tts):
        if 'Yes' in df['Buy'].iloc[i]:
            buying_inds.append(df.iloc[i+1].name)
            for j in range(1,tts+1):
                if df['RSI'].iloc[i + j] > 40:
                    selling_inds.append(df.iloc[i+j+1].name)
                    trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])
                    break
                elif j == tts:
                    selling_inds.append(df.iloc[i+j+1].name)
                    trade_len.append(selling_inds[-1] - buying_inds[-1])
                    #print(buying_inds[-1] - selling_inds[-1])

    return buying_inds, selling_inds, trade_len


def fuckadog():
    for f in range(20,31):
        
        profit_arr, prof_pc, trade_num, avg_trade_len = [[] for _ in range(4)]
        for col in closes.columns: 
            frame = RSIcalc(closes[col], col)
            buy, sell, trade_lens = get_signals(frame, tts=f)
            p = (frame.loc[sell]['Open'].values - frame.loc[buy]['Open'].values) / frame.loc[buy]['Open'].values
            profit_arr.append(np.average(p))
            prof_pc.append(len([i for i in p if i > 0]) / len(p))
            trade_num.append(len(p))
            avg_trade_len.append(np.average(trade_lens))
        
        overall = np.average(profit_arr)*100*50 # for percent and for avg leverage
        win_rate = np.average(prof_pc)
        t = np.average(avg_trade_len)
        ls = [round(i, 3) for i in [overall, win_rate, t]]
        print(ls, f'tts (autosell) = {round(f / 6, 2)} days')
        print('------------------')
    
    return


x = fuckadog()
print(x)








""" 
plt.figure(figsize=(12,5))
plt.scatter(frame.loc[buy].index, frame.loc[buy]['Close'], marker = '^', c='g')
plt.plot(frame['Close'], alpha=0.6)
plt.show()
 """