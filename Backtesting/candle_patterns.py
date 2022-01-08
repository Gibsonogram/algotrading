from cheap_algos import *


def trend_finder(values, n=4):
    """
    params
    ___________ 
    values: to check trend for, usually a moving avg.
    n: number needed to confirm trend either way. Default is 4, as in 4 / 6 needed to confirm.

    """
    up, down = 0,0
    for i,j,k in zip(values, sorted(values), reversed(sorted(values))):
        if up > n:
            return 'uptrend'
        if down > n:
            return 'downtrend'
        if i == j:
            up += 1
        if i == k:
            down += 1




# downtrend reveral patterns
def three_white_soldiers(df):
    dfw = df.iloc[-3:, :]
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # the closes get consecutively higher
    if closes[0] < closes[1] < closes[2]:
        # each day opens within the previous days' range
        if opens[1] <= closes[0] and opens[2] <= closes[1]:
            ispattern = True

    return ispattern


def three_inside_up(df):
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values

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
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # first day is black
    if opens[0] > closes[0]:
        # second day completely engulfs first
        if closes[1] >= opens[0] > opens[1] >= closes[0]:
            # day 3 has higher close than open AND closes higher than second
            if closes[2] > closes[1] and closes[2] > opens[2]:
                ispattern = True
            
    return ispattern


def morning_star(df):
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # first day is black
    if opens[0] > closes[0]:
        # second day gaps down, but can be black or white
        if closes[0] > closes[1] and closes[0] > opens[1]:
            # third day is white and closes higher than midpoint of first
            if closes[2] > opens[2] and closes[2] > (opens[0] + closes[0]) / 2:
                ispattern = True

    return ispattern


# new D.R patterns
def bullish_breakaway(df):
    dfw = df.iloc[-5:, :]
    """
    params: df of which there must be 5 rows.
    It WOULD interact with three_black_crows but alas, it must be in a downtrend, 
    and thus it will never be caught when tbc would be.

    The pattern looks like a 5 candle bowl, with the last candle reversing and ending past the previous 3. 
    """
    ispattern = False
    opens = dfw['Open'].values
    closes = dfw["Close"].values
    if opens[0] > closes[0] > opens[1] > closes[1] >= opens[3] > opens[3]:
        if opens[1] < closes[4]:
            ispattern = True
    return ispattern


def bearish_breakaway(df):
    """
    params: df of which there must be 5 rows.
    It WOULD interact with three_white_soldiers but alas, it must be in an uptrend, 
    and thus it will never be caught when tws would be.

    The pattern looks like a 5 candle inverted bowl, with the last candle reversing and ending past the previous 3. 
    """
    ispattern = False
    opens = df['Open'].values
    closes = df["Close"].values
    if opens[0] < closes[0] < opens[1] < closes[1] <= opens[3] < opens[3]:
        if opens[1] > closes[4]:
            ispattern = True
    return ispattern


def confusing_bearish_three_line_strike(df):
    """
    A 4 candle pattern that theoretically is supposed to be a continuation pattern,
    but historically has acted as a reversal. Must be in downtrend. 
    TBC happens (but in a downtrend so it's not unusual), then a strike of upward momentum closing above first open. 
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # the closes get consecutively lower
    if closes[2] < closes[1] < closes[0]:
        # each day opens within the previous days' range
        if opens[1] >= closes[0] and opens[2] >= closes[1]:
            # final cond beyond TBC
            if closes[3] > opens[0]:
                ispattern = True
    
    return ispattern


def confusing_bullish_three_line_strike(df):
    """
    A 4 candle pattern that theoretically is supposed to be a continuation pattern,
    but historically has acted as a reversal. Must be in uptrend. 
    TWS happens (but in an uptrend so it's not unusual), then a strike of downward momentum closing below first open. 
    """
    ispattern = False
    opens = df["Open"].values
    closes = df["Close"].values
    # the closes get consecutively higher
    if closes[2] > closes[1] > closes[0]:
        # each day opens within the previous days' range
        if opens[1] <= closes[0] and opens[2] <= closes[1]:
            # final cond beyond TWS
            if closes[3] < opens[0]:
                ispattern = True
    
    return ispattern



"""
# bearish continuation
def two_black_gapping(df):
    
    Technically 3 candle pattern, similar to TBC,
    but the first and sceond candles have a gap... that's about it.
    
    pass
"""







# uptrend reversal patterns
def three_black_crows(df):
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # the closes get consecutively lower
    if closes[2] < closes[1] < closes[0]:
        # each day opens within the previous days' range
        if opens[1] >= closes[0] and opens[2] >= closes[1]:
            ispattern = True
    
    return ispattern


def three_inside_down(df):
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
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
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # first day is white
    if closes[0] > opens[0]:
        # second day completely engulfs first
        if opens[1] >= closes[0] > opens[0] >= closes[1]:
            # day 3 has higher open than close AND closes lower than second
            if opens[2] > closes[2] and closes[1] > closes[2]:
                ispattern = True
    
    return ispattern


def evening_star(df):
    dfw = df.iloc[-3:, :]
    """
    We check the conditions for the candle pattern. 
    Assumes the trend has already been found to be down.
    """
    ispattern = False
    opens = dfw["Open"].values
    closes = dfw["Close"].values
    # first day is white
    if closes[0] > opens[0]:
        # second day gaps up, but can be black or white
        if closes[1] > closes[0] and opens[1] > closes[0]:
            # third day is black and closes lower than midpoint of first
            if opens[2] > closes[2] and closes[2] < (closes[0] + opens[0]) / 2:
                ispattern = True
    
    return ispattern

