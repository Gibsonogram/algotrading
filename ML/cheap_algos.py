import numpy as np
import pandas as pd




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



