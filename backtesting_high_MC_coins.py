import pandas as pd

hist_data = pd.DataFrame()

binance_high_MC_coins = ['BTC', 'ETH', 'LTC', 'ADA', 'DASH', 'EOS', 'LINK', 'NEO', 'QTUM', 'XLM', 'ZEC']
for coin in binance_high_MC_coins:
    buttstick = pd.read_csv(f'historical_data/binance_high_MC_coins/Binance_{coin}USDT_1h.csv')
    hist_data.insert(0, coin, buttstick['close'])

# cleaning and reformatting data
hist_data['date'] = buttstick['date']
hist_data = hist_data.iloc[::-1].reset_index(drop=True)
in_position = False
print(hist_data)


# it would be cool if you could take column as an argument, so you could test it against only one coin
def backtest_AAA(initial_betting_money, momentum_period, percent_increase=5, percent_decrease=-1):
    global in_position
    total_profit = 0
    total_profit_forall = 0
    # for col in hist_data.head(rows):
    # add this if you want all columns
    commission_multiplier = 0.99925
    buy_never_sell_total = 0

    for col in hist_data:
        if col == 'date':
            break
        first_trade = True
        in_position = False
        betting_money = initial_betting_money
        print(f'{col} trades start here, betting money reset \n', '\n', '\n')

        for index, entry in enumerate(hist_data[col]):

            date = str(hist_data.at[index, 'date'])
            date_hour = date.split(' ')

            if momentum_period < index < len(hist_data) - 1:
                percent_change = round(((entry - hist_data.at[index - 1, col]) / hist_data.at[index - 1, col]) * 100, 2)

                # calculating momentum by getting an average of the percent changes over some period of time
                momentum = round(((entry - hist_data.at[index - momentum_period, col]) / hist_data.at[index - momentum_period, col]) * 100, 2)

                if percent_change > momentum > percent_increase and not in_position:

                    buy_amount = (betting_money / entry) * commission_multiplier
                    if first_trade:
                        initial_buy = buy_amount
                        first_trade = False
                    buy_price = entry
                    in_position = True

                    print(f"bought {col} at {entry}, on {date_hour[0]}")
                    print(f"at {date_hour[1][:2]}, because it increased {percent_change}% in the last hour\n""")

                if percent_change < percent_decrease and in_position:

                    sell_amount = round(buy_amount * entry * commission_multiplier, 2)
                    sell_price = entry
                    in_position = False

                    date = str(hist_data.at[index, 'date'])
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


backtest_AAA(50, 2, -10, -8)

# print(hist_data['QTUM'])


"""
NOTES:

backtest(momentum_period = 2, percent_increase = 3, percent_decrease= -7):
with this setup, QTUM made more than just holding QTUM,  377 vs 355. XLM was also within $10 of buy and hold strategy. 
This is the first time the strategy has been higher return than buy-hold.

"""

