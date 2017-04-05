from __future__ import division

from scipy.special import expit
import scipy.signal

import peakutils

from measurements import *
from sample import EnvironmentSample
from analyze import *

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
def detrend(es):
	for c in es.channels:
		c.signal = scipy.signal.detrend(c.signal, type='constant')
	return es

@stage(require=[bandpass])
def find_pulse_start_index(es):
	left, right = es.channels
	lps, rps = find_signal_start(
		left.signal, right.signal, left.silence, right.silence,
		cutoff_index=(
			min(1, 2 * (
				es.us_pulse_duration / es.us_record_duration)
			) * len(left.signal))
		)
	)
	left.pulse_start_index = lps
	right.pulse_start_index = rps
	return es

@stage(require=[find_pulse_start_index])
def align_samples(es):
	left, right = es.channels
	left.signal, right.signal = align_samples(
		left.signal, right.signal,
		left.pulse_start_index, right.pulse_start_index
	)
	return es

@stage(require=[find_pulse_start_index])
def normalize(es):
	left, right = es.channels
	take_samples = 0.2 * (us_pulse_duration / 1e6) * es.rate
	left_rms = np.std(left.signal[0:take_samples])
	right_rms = np.std(right.signal[0:take_samples])
	left.signal *= left_rms / right_rms
	# Now make the max sample 1
	max_sample = max(max(left.signal), max(right.signal))
	left.signal = left.signal / max_sample
	right.signal = right.signal / max_sample
	return es

@stage()
def bandpass(es):
	for c in es.channels:
		c.signal = util.bandpass(
			c.signal, es.hz_band[0], es.hz_band[1], es.rate
		)
	return es

@stage(require=[detrend], forbid=[normalize])
def noisereduce(es):
	for c in es.channels:
		c.signal = noise_reduce(
			c.signal.astype(np.float64),
			c.silence.astype(np.float64),
			NoiseReduceSettings()
		)
	return es