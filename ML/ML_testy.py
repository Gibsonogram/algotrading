import numpy as np
import time as t
from sklearn import datasets
from sklearn.model_selection import train_test_split
import matplotlib as mpl
import matplotlib.pyplot as plt
import talib as tl
from ML.ML_algos import LogisticRegression



bc = datasets.load_breast_cancer()
X, y = bc.data, bc.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)


"""
print(X_train.shape)
print(y_train.shape)

fig = plt.figure(figsize=(4, 4))

plt.scatter(X[:, 0], y, color='b', marker='o', edgecolor='k', s=30)
plt.show()
"""


def accuracy(y_true, y_predicted):
    acc = np.sum(y_true == y_predicted) / len(y_true)
    return acc


regressor = LogisticRegression(learning_rate=.00001)
regressor.fit(X_train, y_train)
predictions = regressor.predict(X_test)

print('LR classification accuracy:', round(accuracy(y_test, predictions), 4))
