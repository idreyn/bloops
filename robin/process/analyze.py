from __future__ import division
import random
import peakutils

import numpy as np

def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma



def align(sample):
	window = 1000
	threshold = 0.004
	cutoff_index = max(np.argmax(sample[:,0]), np.argmax(sample[:,1]))
	sample = sample[0:cutoff_index]
	left = moving_average(sample[:,0] ** 2, window)
	right = moving_average(sample[:,1] ** 2, window)
	max_left, max_right = np.max(left), np.max(right)
	left *= 1 / max_left
	right *= 1 / max_right
	return np.argmax(left > threshold) - np.argmax(right > threshold)

