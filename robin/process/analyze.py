from __future__ import division
import random
import peakutils

import numpy as np

def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma

def align(left, right):
	window = 100
	threshold = 0.3
	cutoff_index = max(np.argmax(left), np.argmax(right))
	left = left[0:cutoff_index]
	right = right[0:cutoff_index]
	left = moving_average(left ** 2, window)
	right = moving_average(right ** 2, window)
	max_left, max_right = np.max(left), np.max(right)
	left *= 1 / max_left
	right *= 1 / max_right
	return np.argmax(left > threshold) - np.argmax(right > threshold)

