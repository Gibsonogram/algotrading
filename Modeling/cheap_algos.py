import numpy as np
import pandas as pd



def moving_average(values, period):
    if len(values) < period - 1:
        return print('period is longer than the list')
    # we use (period - 1) because index starts at 0
    if len(values) >= period - 1:
        period_sum = 0
        for i in range(0, period):
            period_sum += values[-1 - i]
        mov_av = round(period_sum / period, 1)

    return mov_av


def ES(series, num_terms, alpha):
    ES_list = []
    if 0 < alpha < 1:
        for index, close in enumerate(series):
            if index <= num_terms:
                ES_list.append(close)
            else:
                term_sum = alpha*close
                normings = [alpha]
                for i in np.arange(1, num_terms - 1):
                    weight = (1 - alpha)**i
                    normings.append(weight)
                    term = np.dot(weight, (series[index - i]))
                    term_sum += term

                normalizer = sum(normings)
                ES = round(term_sum / normalizer, 2)
                ES_list.append(ES)
        return ES_list
    else:
        return 'alpha must be between (0,1)'


def ES_with_pred(series, num_terms, alpha, prediction_horizon=3):
    original = len(series)
    ES_pred = []
    if 0 < alpha < 1:
        x = 1
        for index, close in enumerate(series):
            term_sum = alpha*close
            normings = [alpha]
            if index <= num_terms:
                ES_pred.append(close)
            else:
                
                last = num_terms - x
                for i in np.arange(1, last):
                    weight = (1 - alpha)**(i)
                    normings.append(weight)
                    term = np.dot(weight, (series[index - i]))
                    term_sum += term
                
                    normalizer = sum(normings)
                    ES = round(term_sum / normalizer, 2)

                if original - 1 <= index < original + prediction_horizon:
                    x += 1
                    series.append(ES)
                
                ES_pred.append(ES)
        return ES_pred
    else:
        return 'alpha must be between (0,1)'


def differencing(series, lag):
    diff_closes = []
    for index, close in enumerate(series):
        if index >= lag:
            diff_close = series[index] - series[index - lag]
            diff_closes.append(diff_close)
        else:
            diff_closes.append(0)
    return diff_closes


def inverse_differencing(prediction_series, original_series):
    diff_added_back = []
    for index, val in enumerate(prediction_series):
        if index >= len(original_series):
            true_pred = original_series[-1] + val
            ma_period = 3
            ma_factor = moving_average(original_series[-ma_period:], ma_period) / original_series[-ma_period]
            original_series.append(true_pred * ma_factor)
        diff_added_back.append(original_series[index] + val)
    return diff_added_back
