import pandas as pd


#clean the data
OMG = pd.read_csv('historical_data/low_MC_coins/OMG_hourly.csv')
REP = pd.read_csv('historical_data/low_MC_coins/REP_hourly.csv')
ZRX = pd.read_csv('historical_data/low_MC_coins/ZRX_hourly.csv')
ETC = pd.read_csv('historical_data/low_MC_coins/ETC_hourly.csv')

coins_hourly = ['OMG', 'ETC', 'REP']


df = pd.DataFrame()

df['OMG'] = OMG['close']
df['REP'] = REP['close']
df['ETC'] = ETC['close']
df['date'] = OMG['date']
in_position = False


# so I built a moving average function which is technically more impressive than I meant for it to be.
def moving_average(values, period):
    if len(values) < period - 1:
        return print('period is longer than the list')
    # we use (period - 1) because index starts at 0
    if len(values) >= period - 1:
        period_sum = 0
        for i in range(0, period):
            period_sum += values[-1 - i]
        mov_av = round(period_sum / period, 1)

    return mov_av


little = [10, 24, 43]

moving_average(little, 3)


def backtest_ma(dataframe, betting_money, percent_increase, percent_decrease):
    global in_position
    dataframe = dataframe.head(2000)
    commission_multiplier = 0.99925

    for index, row in dataframe.iterrows():
        date = row[-1]
        percent_change_ls = []
        price_ls = []

        for i, price in enumerate(row[:-1]):
            latest_three = [dataframe.iat[index - 2, i],
                            dataframe.iat[index - 1, i],
                            price]
            ma = moving_average(values=latest_three, period=3)
            percent_change = round((ma - dataframe.iat[index - 2, i]) / dataframe.iat[index - 2, i] * 100, 2)

            # now we do the buy logic
            price_ls.append(price)
            percent_change_ls.append(percent_change)

        column_list = dataframe.columns.to_list()
        percent_change_ls_info = sorted(zip(percent_change_ls, column_list, price_ls))
        highest_gainer = percent_change_ls_info[-1]

        if index > 4:

            # buy after not being in position
            if not in_position:
                # buy conditions
                if highest_gainer[0] > percent_increase:
                    # buy amount is in coin currency obvi
                    buy_amount = (betting_money / highest_gainer[2]) * commission_multiplier
                    in_position = True
                    position_details = [highest_gainer[1], buy_amount]
                    print(f'bought {betting_money} of {highest_gainer[1]} at {highest_gainer[2]} on {date}')

            # sell and switch conditions
            if in_position:

                # sell condition
                if highest_gainer[0] < percent_decrease:
                    in_position = False
                    for i, j, k in percent_change_ls_info:
                        if j == position_details[0]:
                            sell_coin = j
                            sell_price = k
                    sell_amount = buy_amount * sell_price * commission_multiplier
                    print(f'sold {sell_coin} for {sell_amount} on {date}')
                    betting_money = sell_amount


                # switch condition








backtest_ma(df, 50, 3, -3)



"""

        for index, entry in enumerate(df[col]):

            date = str(df.at[index, 'date'])
            date_hour = date.split(' ')

            if momentum_period < index < len(df) - 1:
                percent_change = round(((entry - df.at[index - 1, col]) / df.at[index - 1, col]) * 100, 2)

                # calculating momentum by getting an average of the percent changes over some period of time
                momentum = round(((entry - df.at[index - momentum_period, col]) / df.at[index - momentum_period, col]) * 100, 2)

                if percent_change > momentum > percent_increase and not in_position:

                    buy_amount = (betting_money / entry) * commission_multiplier
                    
                    buy_price = entry
                    in_position = True

                    print(f"bought {col} at {entry}, on {date_hour[0]}")
                    print(f"at {date_hour[1][:2]}, because it increased {percent_change}% in the last hour\n")

                if percent_change < percent_decrease and in_position:

                    sell_amount = round(buy_amount * entry * commission_multiplier, 2)
                    sell_price = entry
                    in_position = False

                    date = str(df.at[index, 'date'])
                    date_hour = date.split(' ')

                    profit = round(sell_amount - betting_money, 2)
                    print(f"sold {col} for {sell_price}, on {date_hour[0]}")
                    print(f"at {date_hour[1][:2]}, because it decreased {percent_change}% in the last hour")
                    print(f"total for this trade is {profit}", '\n', f'betting money is now {sell_amount} \n')
                    total_profit += profit
                    betting_money = sell_amount

        if not in_position:
            total_profit_forall += round(betting_money - initial_betting_money, 2)
            print(f'total_profit for {col} over period is {round(sell_amount, 2)}')
        else:
            total_profit_forall += round(sell_amount, 2)
            print(f'bought and was holding at end, total was {round(buy_amount * entry * commission_multiplier, 2)}')
        buy_never_sell = round(initial_buy * entry * commission_multiplier, 2)
        buy_never_sell_total += buy_never_sell
        print(f'if you had bought and not sold once, total would be {buy_never_sell}')

    print('\n')
    print(f'total for all coins, is {round(total_profit_forall, 2)}')
    print(f'total if you had bought and not sold any is {round(buy_never_sell_total, 2)}')


backtest_small_boys(50, 2, 1, -2)
"""


"""
NOTES:

backtest(momentum_period = 2, percent_increase = 3.3, percent_decrease= -3.2):
OMG vastly outperforms the buy and hold strategy, in fact by an order of magnitude. ETC does as well, however by
only a small amount. REP profits but only $5 while buy and hold strategy gives decent return.

Dip strategies are trash apparently on these coins.

daily charts are simply too slow to catch these momentum spikes that I'm looking for. Even the best strategies are under
half of what the buy and hold strategy yields.  
"""






