from __future__ import division
import random
import peakutils

import numpy as np


def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma        
        
def align(left, right, lsi, rsi):
    offset = lsi - rsi
    if offset < 0:
        offset = 0 - offset
        first_is_left = True
        first = left
        last = right
    else:
        first_is_left = False
        first = right
        last = left
    if offset > 0:
        first = first[:-offset]
        last = last[offset:]
    return first if first_is_left else last, last if first_is_left else first
