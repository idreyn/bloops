import struct
import time
import numpy as np

from scipy.special import expit
from scipy.signal import *

import matplotlib.pyplot as plt
import peakutils

from config import *
from util import *

class Device:
	SPEED_OF_SOUND = 0.343 / 1000 # meters per us
	SPEAKER_MIC_DISTANCE = 1.0 / 6 # about half a foot
	PICKUP_DELAY = SPEAKER_MIC_DISTANCE / SPEED_OF_SOUND # us

class Pulse(object):
	def __init__(self,start,end,duration):
		self.start = start
		self.end = end
		self.ms_duration = duration

	def low(self):
		return min(self.start,self.end)

	def high(self):
		return max(self.start,self.end)

class ChannelSample(object):
	def __init__(
		self,
		sample,
		us_recording_start
	):
		self.sample = sample
		self.us_recording_start = us_recording_start

class EnvironmentSample(object):
	def __init__(
		self,
		channels,
		us_pulse_start,
		us_pulse_duration,
		us_expected_distance=np.inf):
		self.len = len(channels[0].sample)
		self.domain = np.arange(self.len)
		self.channels = channels
		self.us_pulse_duration = us_pulse_duration
		self.us_pulse_start = us_pulse_start
		self.us_expected_distance = us_expected_distance

	def index_to_us(self,ind):
		return 1e6 * ind * 1.0 / RATE

	def us_to_index(self,us_time):
		return int(RATE * us_time * 1.0 / 1e6)
		# ind = 192k * time[s] = RATE

	def process(self):
		assert len(self.channels) == 2
		pre_silence_boundary = self.us_to_index(self.us_pulse_start + Device.PICKUP_DELAY)
		print pre_silence_boundary
		esi = np.inf
		for c in self.channels:
			c.silence = c.sample[0:pre_silence_boundary]
			c.signal = detrend(c.sample[pre_silence_boundary:],type='constant')
			esi = min(esi,echo_start_index(c.signal))
		assert esi < np.inf
		envelope = sigmoid_pulse_envelope(
			self.domain[pre_silence_boundary:] - pre_silence_boundary,
			esi,
			0.5
		)
		print (envelope * self.channels[0].signal).dtype
		return noise_reduce(
			self.channels[0].signal * envelope,
			self.channels[0].silence,
			NoiseReduceSettings()
		)

def to_db(val):
	return 10 * np.log10((0.00000001 + np.abs(val)) ** 2)

def from_db(val):
	return np.power(10,(1.0 / 20) * val)

def trim(arr,start,end=1):
	start_ind = int(round(start * len(arr)))
	end_ind = int(round(end * len(arr)))
	return arr[start_ind:end_ind]

def pad_to_size(sample,length):
	zeroes = np.repeat(0,length - len(sample))
	return np.concatenate((sample,zeroes))

def bandpass_coefficients(lowcut, highcut, fs, order=3):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b,a = butter(order, [low,high], btype='band')
	return b,a

def bandpass(data,low,high):
	bpf = bandpass_coefficients(low,high,RATE)
	return lfilter(bpf[0],bpf[1],data)

def moving_average(sample,size):
	assert size % 2 == 1
	hw = size / 2
	l = len(sample)
	res = np.empty(l)
	total = np.sum(sample[0:hw])
	for center in xrange(l):
		off = center - hw - 1
		on = center + hw + 1
		i0 = max(center - hw,0)
		i1 = min(center + hw + 1,l)
		c = float(size) / (i1 - i0)
		if off >= 0:
			total = total - sample[off]
		if on < l:
			total = total + sample[on]
		res[center] = total * c
	return res

def echo_start_index(sample):
	MIN_DIST = 500
	THRESHOLD = 0.2
	indices = peakutils.indexes(
		sample,
		min_dist=MIN_DIST,
		thres=THRESHOLD
	)
	[p0,p1] = indices[0:2]
	constrained = moving_average(np.abs(sample[p0:p1]),101)
	return np.where(constrained == min(constrained))[0][0]

def sigmoid(x,k=5):
	if -k < x < k:
		return expit(x)
	elif x < 0:
		return 0.0
	else:
		return 1.0
sigmoid = np.frompyfunc(sigmoid,1,1)

def sigmoid_pulse_envelope(domain,start_index,k=0.2):
	return np.array(k + (1 - k) * sigmoid(domain - start_index))

from noisereduce import *