import struct
import time
import numpy as np
from scipy.signal import *
import matplotlib.pyplot as plt
import peakutils

from config import *
from noisereduce import *
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

class EnvironmentSample(object):
	def __init__(
		self,
		left_sample,
		right_sample,
		us_pulse_start,
		us_pulse_duration,
		us_expected_distance=np.inf):
		self.len = len(left_sample)
		self.left_sample = left_sample
		self.right_sample = right_sample
		self.us_pulse_start = us_pulse_start
		self.us_pulse_duration = us_pulse_duration
		self.us_expected_distance = us_expected_distance
		self.us_duration = 1e6 * len(left_sample) / RATE

	def index_to_us(self,ind):
		return 1e6 * ind * 1.0 / RATE

	def us_to_index(self,time):
		return int(RATE * time * 1.0 / 1e6)

	def process(self):
		pre_silence_boundary = us_to_index(self.us_pulse_start + Device.PICKUP_DELAY)
		self.left_silence = self.left_sample[0:pre_silence_boundary]
		self.right_silence = self.right_sample[0:pre_silence_boundary]


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
	t0 = time.time()
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
	print 'moving average:', time.time() - t0
	return res

def find_after_emit(sample):
	t0 = time.time()
	sample = medfilt(np.abs(hilbert(sample)),11)
	print time.time() - t0
	plt.plot(sample)
	plt.show()
	return
	top = np.max(sample)
	print top
	x = np.array(range(len(sample)))
	ind = peakutils.indexes(sample,thres=0.2,min_dist=500)
	plt.plot(top - sample)
	plt.show()
	plt.plot(sample)
	plt.plot(x[ind],sample[ind],'ro')
	plt.show()

def prep_for_playback(sample):
	time = np.array(xrange(len(sample)))
	MIN_DIST = 500
	THRESHOLD = 0.2
	indices = peakutils.indexes(sample,min_dist=MIN_DIST,thres=THRESHOLD)
	[p0,p1] = indices[0:2]
	plt.plot(time,sample)
	plt.plot(time[[p0,p1]],sample[[p0,p1]],'ro')
	plt.show()
	constrained = moving_average(np.abs(sample[p0:p1]),101)
	time_constrained = np.array(xrange(len(constrained)))
	top_ind = np.where(constrained == min(constrained))
	plt.plot(time_constrained,constrained)
	plt.plot(time_constrained[top_ind],constrained[top_ind],'ro')
	plt.show()