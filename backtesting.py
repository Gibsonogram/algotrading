from ast import parse
from datetime import timedelta
from operator import concat
from os import times
from textwrap import indent
from time import time

from numpy.lib.function_base import append
from binance_functions import *
import pandas as pd
import numpy as np
from cheap_algos import *
from dateutil import parser
import warnings
import math

warnings.simplefilter(action='ignore', category=Warning)


def pc_strategy(df, x_highest=9, sell_pc=0):
    """
    Applies percent change strategy to whatever df is given
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
    return res, perc_change_ls, highest_pc.iat[1, -1]


def backtest(start_date, end_date=str(datetime.datetime.today())):
    
    # convert holding period with interval to timedelta that we can use in for loop
    df = all_coin_data('4h', start_date, end_date)

    for x_highest in np.arange(4, 9):
        for sell_pc in range(90, 100, 10):
            for days in range(1,3):
                holding_periods = int((24 / int(parser.parse('4h').hour)) * days)
                percents, pos_pc, stdevs = [], [], []
                for i in range(3, len(df) - holding_periods):
                    window = i+holding_periods
                    window_df = df.iloc[i:window, :]
                    x = pc_strategy(window_df, x_highest=x_highest, sell_pc=sell_pc)
                    if pd.isna(x[0]):
                        continue
                    else:
                        percents.append(x[0])
                        stdevs.append(np.std(x[1]))
                
                # calculate buy and sell fee for each coin, each day.
                binance_fees = round(0.15*(7 / days), 3)

                total_expected_value = np.average(percents)
                total_exp_value_week = (7 / days) * total_expected_value
                final_exp_value_week = round(total_exp_value_week - binance_fees, 2)
                pos_pc = [i for i in percents if i > 0]
                print(f"Holding {days} days, Sell_pc = {sell_pc}%")
                print(f"x_highest: {x_highest}")
                print(f"Expected value[week - fees] = {final_exp_value_week}%")
                print(f"Profits {round(len(pos_pc) / len(percents) * 100, 1)}% of the time.")
                print(f"Standard deviation: {round(np.std(stdevs)*(total_exp_value_week / 100), 3)}")
                print('--------------------')
    return


backtest('1 Jan 2020')