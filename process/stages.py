from scipy.special import expit
from scipy.signal import *

import peakutils

from measurements import *
from sample import EnvironmentSample

def stage(require=None, forbid=None):
	if require is None:
			require = []
	elif not hasattr(require, "__iter__"):
		require = [require]
	if forbid is None:
		forbid = []
	elif not hasattr(forbid, "__iter__"):
		forbid = [forbid]
	def decorator(stage_func):
		def func_wrapper(es):
			if not type(es) is EnvironmentSample:
				raise Exception(
					"Stage %s was not passed an EnvironmentSample" % (
						str(stage_func)
					)
				)
			if not es.passed_stages(require):
				raise Exception(
					"Cannot run pipeline stage %s without first" + \
					" running its require." % (str(stage_func))
				)
			if es.passed_stages(forbid):
				raise Exception(
					"Cannot run pipeline stage %s because a forbidden stage" + \
					" has already been applied." % (str(stage_func))
				)
			es = stage_func(es)
			if not type(es) is EnvironmentSample:
				raise Exception(
					"Stage %s did not return an EnvironmentSample" % (
						str(stage_func)
					)
				)
			es.pass_stage(stage_func)
			return es
		return func_wrapper
	return decorator

@stage
def split_silence(es):
	def us_to_index(es, us_time):
		return int(es.rate * us_time * 1.0 / 1e6)
	pre_silence_boundary = es.us_to_index(
		es.us_pulse_start + Measurements.PICKUP_DELAY)
 	if pre_silence_boundary > len(es.channels[0].sample):
 		raise Exception()
	for c in es.channels:
		c.silence = c.sample[0:pre_silence_boundary]
	return es

@stage
def detrend(es):
	for c in es.channels:
		c.signal = detrend(c.sample[pre_silence_boundary:], type='constant')
	return es

@stage(require=[split_silence])
def bandpass(es):
	for c in es.channels:
		c.signal = bandpass(c.signal, es.hz_band[0], es.hz_band[1], es.rate)
	return es

@stage(require=[split_silence, detrend])
def noisereduce(es):
	for c in es.channels:
		c.signal = noise_reduce(
			c.signal.astype(np.float64),
			c.silence.astype(np.float64),
			NoiseReduceSettings()
		)
	return es

@stage(forbid=[bandpass])
def align_samples(es):
	MIN_DIST = 500
	THRESHOLD = 0.3
	for c in es.channels:
		indices = peakutils.indexes(
			c.signal,
			min_dist=MIN_DIST,
			thres=THRESHOLD
		)
		c.peak = max(indices)
	[first, last] = sorted(
		es.channels,
		key=lambda c: c.peak
	)
	cutoff = last.peak - first.peak
	first.signal = first.signal[:-cutoff]
	last.signal = last.signal[cutoff:]
	return es