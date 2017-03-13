import struct
import time
import numpy as np

from scipy.special import expit
from scipy.signal import *

import peakutils

from util import *

SPEED_OF_SOUND = 0.343 / 1000 # meters per us

class Measurements:
	SPEAKER_MIC_DISTANCE = 1.0 / 6 # about half a foot
	PICKUP_DELAY = SPEAKER_MIC_DISTANCE / SPEED_OF_SOUND # us

class ChannelSample(object):
	def __init__(
		self,
		sample,
		us_recording_start=0
	):
		self.sample = sample
		self.us_recording_start = us_recording_start
		self.signal = None
		self.peak = None
		self.silence = None

class EnvironmentSample(object):
	def __init__(
			self,
			sample,
			rate,
			us_pulse_start,
			us_pulse_duration=None,
			us_expected_distance=np.inf):
		self.channels = [ChannelSample(sample[:,0]), ChannelSample(sample[:,1])]
		self.rate = rate
		self.us_pulse_duration = us_pulse_duration
		self.us_pulse_start = us_pulse_start
		self.us_expected_distance = us_expected_distance

	def us_to_index(self, us_time):
		return int(self.rate * us_time * 1.0 / 1e6)

	def process(self):
		# Sorry, guy
		assert len(self.channels) == 2
	 	self.split_silence()
	 	self.align_samples()
	 	self.bandpass()
	 	return self.merge()

	def split_silence(self):
		pre_silence_boundary = self.us_to_index(self.us_pulse_start + Measurements.PICKUP_DELAY)
	 	if pre_silence_boundary > len(self.channels[0].sample):
	 		raise Exception()
	 	# Remove DC component
		for c in self.channels:
			c.silence = c.sample[0:pre_silence_boundary]
			c.signal = detrend(c.sample[pre_silence_boundary:], type='constant')
		return self.channels

	def bandpass(self):
		for c in self.channels:
			c.signal = bandpass(c.signal, 50000, 80000, self.rate)
		return self.channels

	def noisereduce(self):
		for c in self.channels:
			c.signal = noise_reduce(
				c.signal.astype(np.float64),
				c.silence.astype(np.float64),
				NoiseReduceSettings()
			)
		return self.channels

	def align_samples(self):
		MIN_DIST = 500
		THRESHOLD = 0.3
		for c in self.channels:
			indices = peakutils.indexes(
				c.signal,
				min_dist=MIN_DIST,
				thres=THRESHOLD
			)
			c.peak = max(indices)
		[first, last] = sorted(
			self.channels,
			key=lambda c: c.peak
		)
		cutoff = last.peak - first.peak
		first.signal = first.signal[:-cutoff]
		last.signal = last.signal[cutoff:]
		return self.channels

	def merge(self):
		res = np.empty((
			len(self.channels[0].signal),
			len(self.channels)
		), dtype=np.int16)
		for i, c in enumerate(self.channels):
			res[:,i] = c.signal.astype(np.int16)
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
	constrained = moving_average(np.abs(sample[p0:p1]), 101)
	return np.where(constrained == min(constrained))[0][0]
