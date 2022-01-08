from cheap_algos import *


 
def trend_finder(values):
    """Takes a list of values to find the trend of.
    ------------------------------------
    Returns str 'uptrend', 'downtrend' or returns None"""

    up, down = 0,0
    for i,j,k in zip(values, sorted(values), reversed(sorted(values))):
        if up > 4:
            return 'uptrend'
        if down > 4:
            return 'downtrend'
        if i == j:
            up += 1
        if i == k:
            down += 1



# downtrend reversal patterns
def three_white_soldiers(df):
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # the closes get consecutively higher
    if closes[0] < closes[1] < closes[2]:
        # each day opens within the previous days' range
        if opens[1] <= closes[0] and opens[2] <= closes[1]:
            ispattern = True

    return ispattern


def three_inside_up(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values

    # fist day is black
    if opens[0] > closes[0]:
        # middle day is contained in body of first day
        a = opens[0] >= opens[1] > closes[0]
        b = opens[0] > closes[1] >= closes[0]
        if a ^ b:
            # day 3 closes higher than open AND closes above first open
            if closes[2] > opens[0] and closes[2] > opens[2]:
                ispattern = True
    
    return ispattern


def three_outside_up(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # first day is black
    if opens[0] > closes[0]:
        # second day completely engulfs first
        if closes[1] >= opens[0] > opens[1] >= closes[0]:
            # day 3 has higher close than open AND closes higher than second
            if closes[2] > closes[1] and closes[2] > opens[2]:
                ispattern = True
            
    return ispattern


def morning_star(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # first day is black
    if opens[0] > closes[0]:
        # second day gaps down, but can be black or white
        if closes[0] > closes[1] and closes[0] > opens[1]:
            # third day is white and closes higher than midpoint of first
            if closes[2] > opens[2] and closes[2] > (opens[0] + closes[0]) / 2:
                ispattern = True

    return ispattern


def three_stars_south(df):
    pass


# uptrend reveral patterns
def three_black_crows(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be up.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # the closes get consecutively lower
    if closes[2] < closes[1] < closes[0]:
        # each day opens within the previous days' range
        if opens[1] >= closes[0] and opens[2] >= closes[1]:
            ispattern = True
    
    return ispattern


def three_inside_down(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be up.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # first day has higher close than open.
    if closes[0] > opens[0]:
        # middle day is contained in body of first day
        a = closes[0] > opens[1] >= opens[0]
        b = closes[0] >= closes[1] > opens[0]
        if a ^ b:
            # day 3 closes lower than open AND closes below first open
            if opens[2] > closes[2] and opens[0] > closes[2]:
                ispattern = True
    
    return ispattern


def three_outside_down(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be up.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # first day is white
    if closes[0] > opens[0]:
        # second day completely engulfs first
        if opens[1] >= closes[0] > opens[0] >= closes[1]:
            # day 3 has higher open than close AND closes lower than second
            if opens[2] > closes[2] and closes[1] > closes[2]:
                ispattern = True
    
    return ispattern


def evening_star(df):
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be up.
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # first day is white
    if closes[0] > opens[0]:
        # second day gaps up, but can be black or white
        if closes[1] > closes[0] and opens[1] > closes[0]:
            # third day is black and closes lower than midpoint of first
            if opens[2] > closes[2] and closes[2] < (closes[0] + opens[0]) / 2:
                ispattern = True
    
    return ispattern




# downtrend reversals
"""
Three stars in the South: 100% -- which is just slight variation on three-white-soldiers
Breakaway, bearish: 89%
Three white soldiers: 84%
Three-line strike, bullish: 83%
Engulfing, bearish: 82%
Three black crows: 79%
Three-line strike, bearish: 77%
Three outside up: 74%
Upside gap three methods: 72%
Identical three crows: 72%
"""





# continuation patterns
def mat_hold(df):
    # will take in 5 candles
    pass

"""
Mat hold: 78%
Deliberation: 77%
Concealing baby swallow: 75%
Rising three methods: 74%
Separating lines, bullish: 72%
Falling three methods: 71%
Doji star, bearish: 69%
Last engulfing top: 68%
Two black gapping candles: 68%
Side-by-side white lines, bullish: 66%
"""