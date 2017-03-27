from __future__ import division
import signal, sys
import math

import numpy as np
from scipy.signal import *

# Audio processing must-haves

def round_to_nearest(x, base):
	return base * round(x/ base)

def ceil_to_nearest(x, base):
	return base * math.ceil(x / base)

def floor_to_nearest(x, clip):
	return base * math.floor(x / clip)

def log(x, cb):
	print(cb(x))
	return x

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

def zero_pad(sample, left_length=0, right_length=0):
	return np.pad(sample, ((left_length, right_length), (0,0)), mode='constant')

def zero_pad_power_of_two(sample):
	next_power = 2 ** math.ceil(math.log(len(sample), 2))
	print len(sample), next_power
	return zero_pad(sample, right_length=(next_power - len(sample)))

# Python kludges

RUNNING = True

def handle_close():
	def signal_handler(signal, frame):
		kill_app()
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)

def get_ip_address():
	import socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8',80))
		return s.getsockname()[0]
	except:
		return "unavailable"

