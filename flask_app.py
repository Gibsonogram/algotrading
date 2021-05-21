from typing import ChainMap
from flask import *
from os import write
from binance.helpers import interval_to_milliseconds
import config, csv
from binance.client import Client
from binance.enums import *
from binance_testing import *


app = Flask(__name__)
client = Client(config.API_KEY, config.API_SECRET, tld='us')



@app.route("/")
def index():
    title= 'Coinview'
    print(client)
    info = client.get_account()
    balances = info['balances']

    return render_template('index.html', title=title, my_balances=balances)

# other endpoints
@app.route("/buy")
def buy():
    return 'pasta'

@app.route('/sell')
def sell():
    return 'selling'

@app.route('/history')
def history():

    processed_candlesticks = []
    for data in candlesticks:
        candlestick = { 
            'time': data[0] / 1000, 
            'open': data[1], 
            'high': data[2], 
            'low': data[3], 
            'close': data[4]
            }
        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)
