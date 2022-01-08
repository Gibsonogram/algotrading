import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))


# weekly
capital = 10000
betting = capital / 5
avg_growth = 0.023
# this is without capital gains tax which is around 15% for me with values this low.

weeks = range(1,53)
exp = [betting*(1+avg_growth)**(week) for week in weeks]

plt.plot(exp)
plt.show()