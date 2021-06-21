from typing import ChainMap
from flask.app import *
from flask.templating import render_template
from flask import jsonify, redirect, url_for, request
import config, csv
# from binance.client import Client
# from binance.enums import *
# from binance_testing import *


app = Flask(__name__)
# client = Client(config.API_KEY, config.API_SECRET, tld='us')

# pages

@app.route("/")
def index():

    # title= 'Coinview'
    # print(client)
    # info = client.get_account()
    # balances = info['balances']

    return render_template('index.html')

@app.route("/twopol", methods=['GET', 'POST'])
def two_col():
    title= 'two col'
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))
    return render_template('two_col.html', title=title)


@app.route("/wsbscraper")
def wsb_scraper():
    title= 'wsb scraper'
    return render_template('wsbscraper.html', title=title)


"""
# other endpoints
@app.route("/buy", methods=['GET', 'POST'])
def buy():
    return 'pasta'

@app.route('/sell')
def sell():
    return 'selling'


# this is where the data for chart is stored
@app.route('/history')
def history():
    processed_candlesticks = [coin]
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
 """