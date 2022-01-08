import pandas as pd
import numpy as np
import math


def head_and_shoulders(df):
    """
    Param: Takes dataframe with column 'Close'
    _________________
    Returns: bool (ispattern)
    """
    ispattern = False
    closes = df['Close'].values
    

