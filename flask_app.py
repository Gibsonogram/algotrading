from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return 'hareeeeeeeeem'

# other endpoints
@app.route("/buy")
def buy():
    return 'pasta'

@app.route('/sell')
def sell():
    return 'selling'
