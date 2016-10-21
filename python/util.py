from __future__ import division
from math import floor, ceil
import signal, sys

import numpy as np
from scipy.signal import *

# Audio processing must-haves

def round_to_nearest(x, base):
	return base * round(x/ base)

def ceil_to_nearest(x, base):
	return base * ceil(x / base)

def floor_to_nearest(x, clip):
	return base * floor(x / clip)

def log(x, cb):
	print(cb(x))
	return x

def resample(sample, from_rate, to_rate):
	if from_rate == to_rate:
		return sample
	return resample(
		sample,
		len(sample) * (to_rate / from_rate)
	)

def to_db(val):
	return 10 * np.log10((0.00000001 + np.abs(val)) ** 2)

def from_db(val):
	return np.power(10,(1.0 / 20) * val)

def bandpass_coefficients(lowcut, highcut, fs, order=1):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low,high], btype='bandpass')
	return b, a

def bandpass(data, low, high, rate):
	bpf = bandpass_coefficients(low, high, rate)
	return lfilter(bpf[0], bpf[1],data)

def t_axis(sample, rate):
	return np.linspace(0, len(sample) / rate, len(sample))

# Python kludges

def handle_close():
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
