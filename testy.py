import math
import numpy as np


stupid = '3456.789'

# I want to make an algo for greatest common subsequence

item1 = 'fish'
item2 = 'fosh'

# Dynamic Programming implementation of LCS problem

def lcs(X, Y):
    # find the length of the strings
    m = len(X)
    n = len(Y)

    # creating an array
    L = [[None]*(n + 1) for i in range(m + 1)]

    """Following steps build L[m + 1][n + 1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0 :
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]
# end of function lcs

arr1 = [1, 2, 3, 4, 5]
array2 = reduce(lambda x, y: x+y, arr1)
print(array2)




lcs(item1, item2)