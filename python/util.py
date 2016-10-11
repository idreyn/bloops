from __future__ import division
from math import floor, ceil
import signal, sys

from scipy.signal import resample

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


def handle_close():
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)