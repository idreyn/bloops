from __future__ import division

import numpy as np
from scipy.special import expit
import scipy.signal
import peakutils

from measurements import *
from sample import EnvironmentSample
from analyze import align

import util

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
		setattr(stage_func, "__stage__", True)
		def func_wrapper(es):
			if not type(es) is EnvironmentSample:
				raise Exception(
					"Stage %s was not passed an EnvironmentSample" % (
						stage_func.__name__
					)
				)
			if not es.passed_stages(require):
				raise Exception(
					("Cannot run pipeline stage %s without first" + \
					" running its required stages.") % (stage_func.__name__)
				)
			if len(forbid) > 0 and es.passed_stages(forbid):
				raise Exception(
					("Cannot run pipeline stage %s because a forbidden stage" + \
					" has already been applied.") % (stage_func.__name__)
				)
			es = stage_func(es)
			if not type(es) is EnvironmentSample:
				raise Exception(
					"Stage %s did not return an EnvironmentSample" % (
						stage_func.__name__
					)
				)
			es.pass_stage(stage_func)
			return es
		return func_wrapper
	return decorator

@stage()
def stats(es):
	for i, c in enumerate(es.channels):
		c.max_val = max(c.signal)
		c.argmax = np.argmax(c.signal)
		c.avg_power = sum(c.signal ** 2) / len(c.signal)
		print "channel %s: max %s argmax %s avg_power %s" % (i, c.max_val, c.argmax, c.avg_power)
	return es

@stage()
def split_silence(es):
	for c in es.channels:
		c.signal = c.sample
	return es
	# TODO
	def us_to_index(es, us_time):
		return int(es.rate * us_time * 1.0 / 1e6)
	pre_silence_boundary = us_to_index(
		es, es.us_pulse_start + PICKUP_DELAY)
 	if pre_silence_boundary > len(es.channels[0].sample):
 		raise Exception()
	for c in es.channels:
		c.silence = c.sample[0:pre_silence_boundary]
	return es

@stage()
def detrend(es):
	for c in es.channels:
		c.signal = scipy.signal.detrend(c.signal, type='constant')
	return es

@stage()
def bandpass(es):
	for c in es.channels:
		c.signal = util.bandpass(c.signal, es.hz_band[0], es.hz_band[1], es.rate)
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

@stage()
def normalize_samples(es):
	max_val = max([max(c.signal) for c in es.channels])
	for c in es.channels:
		c.signal *= max_val / max(c.signal)
	return es


@stage(forbid=[bandpass])
def align_samples(es):
	left = es.channels[0]
	right = es.channels[1]
	if False:
		cutoff = align(left.signal, right.signal)
	else:
		cutoff = left.argmax - right.argmax
	print cutoff
	if cutoff < 0:
		cutoff = 0 - cutoff
		first = left
		last = right
	else:
		first = right
		last = left
	if cutoff > 0:
		first.signal = first.signal[:-cutoff]
		last.signal = last.signal[cutoff:]
	return es