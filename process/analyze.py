from __future__ import division
import random

import numpy as np
import matplotlib.pyplot as plt

def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma

def align(sample, pulse, region):
	left = sample[:,0]
	right = sample[:,1]
	offset = random.uniform() * region / 2
	energy = 100
	while energy > 1:
		

