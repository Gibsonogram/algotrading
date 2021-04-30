import pandas as pd

binance_coins = ['BTC', 'ETH', 'LTC', 'ADA', 'DASH', 'EOS', 'LINK', 'NEO', 'QTUM', 'XLM', 'ZEC']

hist_data = pd.DataFrame()

for coin in binance_coins:
    buttstick = pd.read_csv(f'historical_data/Binance_{coin}USDT_1h.csv')
    hist_data.insert(0, coin, buttstick['close'])

hist_data['date'] = buttstick['date']
in_position = False

hist_data = hist_data.iloc[::-1].reset_index(drop=True)
print(hist_data)


# it would be cool if you could take column as an argument, so you could test it against only one coin
def backtest(initial_betting_money, percent_increase=5, percent_decrease=-1):
    global in_position
    total_profit = 0
    total_profit_forall = 0
    # for col in hist_data.head(rows):
    # add this if you want all columns
    commission_multiplier = 0.99925

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

            if 1 < index < len(hist_data) - 1:
                momentum = ((entry - hist_data.at[index - 1, col]) / hist_data.at[index - 1, col]) * 100
                momentum = round(momentum, 2)

                if momentum > percent_increase and not in_position:

                    buy_amount = (betting_money / entry) * commission_multiplier
                    if first_trade:
                        initial_buy = buy_amount
                        first_trade = False
                    buy_price = entry
                    in_position = True

                    print(f"bought {col} at {entry}, on {date_hour[0]}")
                    print(f"at {date_hour[1][:2]}, because it increased {momentum}% in the last hour\n""")

                if momentum < percent_decrease and in_position:

                    sell_amount = round(buy_amount * entry * commission_multiplier, 2)
                    sell_price = entry
                    in_position = False

                    date = str(hist_data.at[index, 'date'])
                    date_hour = date.split(' ')

                    profit = round(sell_amount - betting_money, 2)
                    if profit < 0:
                        print(f'the trade on {date_hour} was negative, profit was {profit}')
                    print(f"sold {col} for {sell_price}, on {date_hour[0]}")
                    print(f"at {date_hour[1][:2]}, because it decreased {momentum}% in the last hour")
                    print(f"total for this trade is {profit}", '\n', f'betting money is now {sell_amount} \n')
                    total_profit += profit
                    betting_money = sell_amount

        print(f'total_profit for {col} over period is {round(betting_money - initial_betting_money, 2)}')
        total_profit_forall += total_profit
        print(f'If you had simply bought and held, it would be {round(hist_data.at[index - 1, col] * initial_buy, 2)}')

    print(round(total_profit_forall, 2))


backtest(50, 2, -4)


"""
what tf am I learning???
well it seems to me that 10% jump is too much to look for, because this is the move after the momentum has built.
What I need to find is what percentage moves historically ramp up to a bigger move.
i.e. what I should look for is two--four hours of consecutive percentages above x-percent. 
These would be the moves I want to capitalize on. 

Distill this down to a potential gain/loss. 
"""

