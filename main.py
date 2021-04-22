import websocket, json, pprint
import numpy as np
import pandas as pd


coin = 'btcusd'
c_time = '1m'

SOCKET = f'wss://stream.binance.us:9443/ws/{coin}@kline_{c_time}'

def on_open(ws):
        print('connection opened')

def on_close(ws):
        print('connection closed')

def on_message(ws, message):
        json_message = json.loads(message)
        #this si where the bulk of the stuffffffff is gonne happen
        candle = json_message['k']
        # inside candle json object 'k' we have all of the properties
        is_candle_closed = candle['x']
        close = candle['c']
        close = round(float(close)), 2

        if is_candle_closed:
            print(f'candle closed at {close}')

def on_error(ws, error):
        print(error)

ws = websocket.WebSocketApp(SOCKET,
                            on_open = on_open,
                            on_error = on_error,
                            on_message = on_message,
                            on_close = on_close
                            )

ws.run_forever()

