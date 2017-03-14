from __future__ import division
import random
import peakutils

import numpy as np

def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma



def align(sample):
	window = 100
	threshold = 0.001
	left = moving_average(sample[:,0] ** 2, window)
	right = moving_average(sample[:,1] ** 2, window)
	left -= peakutils.baseline(left, 2)
	right -= peakutils.baseline(right, 2)
	max_left, max_right = np.max(left), np.max(right)
	left *= 1 / max_left
	right *= 1 /max_right
	return np.argmax(left > threshold) - np.argmax(right > threshold)

