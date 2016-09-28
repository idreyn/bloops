from __future__ import division
from math import floor, ceil
import signal, sys

def round_to_nearest(x, base):
	return base * round(x/ base)

def ceil_to_nearest(x, base):
	return base * ceil(x / base)

def floor_to_nearest(x, clip):
	return base * floor(x / clip)

def de_interleave(arr):
	a = []
	b = []
	for i, x in enumerate(arr):
		if i % 2 == 0:
			a.append(x)
		else:
			b.append(x)
	return a,b

def log(x, cb):
	print(cb(x))
	return x

def handle_close():
	def signal_handler(signal, frame):
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)