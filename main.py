import websocket, json, talib
import numpy as np
import config
from binance.enums import *
import binance.client

Client = binance.client.Client

RSI_PERIOD = 14
RSI_oversold = 30
RSI_overbought = 70
COIN = 'uniusd'
candle_interval = '1m'

TRADE_SYMBOL = 'UNIUSD'
TRADE_QUANTITY = 0.5


# I will use this to determine if my bot has already bought or not. I don't want to buy every minute.
# I just want to buy once.

in_position = False

# this gets the keys from config.py file which is .gitignored for my safety.
client = Client(config.API_KEY, config.API_SECRET, tld = 'us')

SOCKET = f'wss://stream.binance.us:9443/ws/{COIN}@kline_{candle_interval}'

# in order of params this function says buy/sell quantity of symbol with order type
def order(side, quantity, symbol, type = ORDER_TYPE_MARKET):
    try:
        print('sending order')
        order = client.create_order(symbol = symbol,
                                    side = side,
                                    type = type,
                                    quantity = quantity)
        print(order)
    except Exception as e:
        return False

    return True


def on_open(ws):
    print('connection opened')


def on_close(ws):
    print('connection closed')


# we will use this list to apply RSI indicator
closes = []


def on_message(ws, message):
    json_message = json.loads(message)
    # this is where the bulk of the stuffffffff is gonne happen
    candle = json_message['k']
    # inside candle json object 'k' we have all of the properties
    is_candle_closed = candle['x']
    close = candle['c']
    close = round(float(close), 2)

    if is_candle_closed:
        print(f'candle closed at {close}')
        closes.append(close)
        print(closes)

        if len(closes) >= RSI_PERIOD:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)

            last_rsi = rsi[-1]
            print(f'the last rsi is {last_rsi}')

            if last_rsi > RSI_overbought:
                if in_position:
                    print('sell that shit!!!')
                    # binance API sell logic
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)

                    if order_succeeded:
                        in_position = False
                else:
                    print('nothing to sell here.')

            if last_rsi < RSI_oversold:
                if in_position:
                    print("oversold but you've already bought it.")
                else:
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
                    print('buy that shit!')
                    # TELL BINANCE API TO BUY


def on_error(ws, error):
    print(error)


ws = websocket.WebSocketApp(SOCKET,
                            on_open=on_open,
                            on_error=on_error,
                            on_message=on_message,
                            on_close=on_close
                            )

ws.run_forever()
