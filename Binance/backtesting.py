from binance_functions import *
import pandas as pd
import numpy as np
from cheap_algos import *
import warnings

warnings.simplefilter(action='ignore', category=Warning)

def pc_strategy(df, x_highest=5, sell_pc=100):
    """
    Applies percent_change strategy to whatever df is given
    """

    change_arr = []
    for col in df.columns[:-1]:
        values = df[col].values

        coin_change = percent_change(values[0], values[1])
        change_arr.append([col, coin_change])
        # sort by highest percent change, put that first.
    change_arr.sort(key = lambda x: x[1], reverse=True)

    # highest x perc changes on the buy_date
    highest_changers = change_arr[:x_highest]
    highest_pc = df[[i for (i,j) in highest_changers if j > 0]]
    highest_pc["Date"] = df.iloc[:, -1]

    # sell if coin dips below x_percent
    perc_change_ls = []
    for col in highest_pc.columns[:-1]:
        values = highest_pc[col].values
        for val in values:
            x = percent_change(values[1], val)
            if x < -sell_pc:
                perc_change_ls.append(x)
                highest_pc.drop(col, axis=1, inplace=True)
                break
    
    # for the remaining cols, add their pc at the end of the holding period
    for i, j in list(zip(highest_pc.iloc[1,:-1], highest_pc.iloc[-1,:-1])):
        x = percent_change(i,j)
        perc_change_ls.append(x)
    
    

    res = round(np.average(perc_change_ls), 3)
    return res, perc_change_ls, highest_pc.iat[1, -1], highest_pc



def sma_strategy(df, ma_period, x_highest=5, buy_pc=0, sell_pc=100):
    """Applies simple moving average strategy to whatever df is given
    
    Params
    ----------
    buy_pc: this corresponds to how much higher the last entry has to be above the moving average,
    for you to initiate a buy
    """
    change_arr = []
    for col in df.columns[:-1]:
        values = df[col].values

        # the following would (theoretically) indicate an upward trend
        #if values[ma_period-2] < values[ma_period-1] < values[ma_period]:
        pc_sma = percent_change(np.average(values[:ma_period]), values[ma_period])
        change_arr.append([col, pc_sma])
    
    # sort by highest percent change, put that first.
    change_arr.sort(key = lambda x: x[1], reverse=True)

    # create highest change df
    highest_changers = change_arr[:x_highest]
    highest_pc = df[[i for (i,j) in highest_changers if j > buy_pc]]
    highest_pc["Date"] = df.iloc[:, -1]

    # sell if coin dips below x_percent
    # create whatever condition here
    perc_change_ls = []
    """
    for col in highest_pc.columns[:-1]:
        values = highest_pc[col].values
        for val in values:
            x = percent_change(values[1], val)
            if x < -sell_pc:
                perc_change_ls.append(x)
                highest_pc.drop(col, axis=1, inplace=True)
                break
    """
    # Get the percent change
    for i, j in list(zip(highest_pc.iloc[ma_period,:-1], highest_pc.iloc[-1,:-1])):
        x = percent_change(i,j)
        perc_change_ls.append(x)
    
    
    res = round(np.average(perc_change_ls), 3)
    return res, perc_change_ls


def volume_strategy(df, price_increase, sell_cond):
    """
    Applies volume strategy to df given. Df must have vol col. 
    Interval must be short to catch these boys. 30m to 1h
    
    ASSUMES df cols are of form ["Close", "Volume"] 
    
    """
    volumes = df["Volume"].values
    bought = False
    ls = []
    for index, vol in enumerate(volumes):
        if index > 1:
            price_pc = percent_change(df.iat[index-2, 0], df.iat[index, 0])
            

            # condition to buy
            if bought == False:
                vol_pc = percent_change(volumes[index - 2], vol)
                if vol_pc > 100 and price_pc > price_increase:

                    # theoretically, you'd buy the open of the next candle, 
                    # but the close of the one you just checked suffices.
                    buy_price = df.iloc[index, 0]
                    bought = True
            
            # condition to sell
            else:
                if price_pc < sell_cond:
                    sell_price = df.iat[index, 0]
                    p = percent_change(buy_price, sell_price)
                    ls.append(p)
                    bought = False
                    # print(sell_price)
    
    if len(ls) > 0:
        pos_pc = [i for i in ls if i > 0]
        win_pc = round(len(pos_pc) / len(ls), 2)
        profit_pc = round(np.average(ls), 3)
        return (profit_pc, win_pc, len(ls))

def backtest_any(coin, interval, start_date, end_date=str(datetime.datetime.today())):
    df = get_coin_data(coin, interval, start_date, end_date)
    for sell_pc in np.arange(1, 3.5, 0.5):
        for price_inc in range(6, 15):
            x = volume_strategy(df, price_inc, sell_pc)
            print([x, f"Sell_pc = {sell_pc}, price_inc = {price_inc}"])
        print('-----------------------')



def backtest_all_pc_strategy(start_date, end_date=str(datetime.datetime.today())):
    
    # convert holding period with interval to timedelta that we can use in for loop
    df = all_coin_data('4h', start_date, end_date)
    ma_period = 5
    holding_periods = 5
    for buy_pc in np.arange(8, 10, 1):
        for x_highest in range(4,5):    
            # it's gonna get fucky wucky here:
            # ma_period is the values over which the sma is calculated (this is certainly a parameter)
            # hours = time holding coin(s)
            # holding_periods = conversion of how many periods that many hours crspds to for given interval
            # window = (i + ma_period + holding_periods) where i is whatever row you're on.
            # holding_periods = int(hours)
            percents, pos_pc, stdevs = [], [], []

            for i in range(1, len(df) - (ma_period + holding_periods)):
                
                window = i + (ma_period+1) + holding_periods
                # we use (ma_period+1) because the entire ma_period is used for calculation.
                # we want the NEXT entry to be the first "holding_period," thus we add one.
                window_df = df.iloc[i:window, :]
                x = sma_strategy(window_df, ma_period, x_highest=x_highest, buy_pc=buy_pc)
                if pd.isna(x[0]):
                    continue
                else:
                    percents.append(x[0])
                    stdevs.append(np.std(x[1]))
            
            # calculate buy and sell fee for each coin, each day.
            binance_fees = 0.15

            expected_value = np.average(percents)
            expected_value_week = 7 * (expected_value - binance_fees)
            final_exp_value_week = round(expected_value, 2)
            pos_pc = [i for i in percents if i > 0]
            print(len(pos_pc), len(percents))
            print(f"Holding {x_highest} for {ma_period*4} hours")
            print(f"Buy percent {buy_pc}, ma is {ma_period} periods")
            print(f"Expected value[week] = {final_exp_value_week}%")
            print(f"Profits {round(len(pos_pc) / len(percents) * 100, 1)}% of the time.")
            print(f"Standard deviation: {round(np.std(stdevs)*(expected_value_week / 100), 3)}")
            print('--------------------')
        print('---------------------------')
    return


def backtest(start_date, end_date=str(datetime.datetime.today())):
    df = all_coin_data('4h', start_date, end_date)

    for buy_pc in np.arange(0, 15, 5):
        profit_pc, win_pc = [], []
        holding_period = 12
        for ind in range(2, len(df) - holding_period+1):
            window_df = df.iloc[ind:ind+holding_period+1, :]
            x = pc_strategy(window_df)
            profit_pc.append(x[0])
            win_pc.append(x[1])
    
        prof = round(np.average(profit_pc), 2)
        #win_pc = [float(i) for i in win_pc]
        #win = round(np.average(win_pc*100), 3)
        print(f"Avg profit would be {prof}%")
        #print(f"Wins {win}% of the time.")
        print(f"Buys if {buy_pc}%, holds for {holding_period}")
        print("-----------------------")
    return



backtest_all_pc_strategy('1 October 2021')
