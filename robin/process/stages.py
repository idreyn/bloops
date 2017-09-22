from __future__ import division

import numpy as np
from scipy.special import expit
import scipy.signal
import peakutils

import analyze
import util
from noisereduce import *
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
                        stage_func.__name__
                    )
                )
            if not es.passed_stages(require):
                raise Exception(
                    ("Cannot run pipeline stage %s without first" +
                     " running its required stages.") % (stage_func.__name__)
                )
            if len(forbid) > 0 and es.passed_stages(forbid):
                raise Exception(
                    ("Cannot run pipeline stage %s because a forbidden stage" +
                     " has already been applied.") % (stage_func.__name__)
                )
            es = stage_func(es)
            if not type(es) is EnvironmentSample:
                raise Exception(
                    "Stage %s did not return an EnvironmentSample" % (
                        stage_func.__name__
                    )
                )
            es.pass_stage(stage_func.__stage__)
            return es
        setattr(stage_func, "__stage__", func_wrapper)
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
def bandpass(es):
    for c in es.channels:
        c.signal = util.bandpass(
            c.signal, es.hz_band[0], es.hz_band[1], es.rate
        )
    return es


@stage()
def detrend(es):
    for c in es.channels:
        c.signal = scipy.signal.detrend(c.signal, type='constant')
    return es

@stage()
def calibrate(es):
    pulse_length = int(es.rate * 1e-6 * es.us_pulse_duration)
    for c in es.channels:
        c.power = analyze.moving_average(c.signal ** 2, pulse_length)
        c.pulse_end_index = np.argmax(c.power) 
        c.pulse_start_index = c.pulse_end_index - pulse_length
    return es

@stage(require=[calibrate])
def align(es):
    left, right = es.channels
    left.signal, right.signal = analyze.align(
        left.signal,
        right.signal,
        left.pulse_start_index,
        right.pulse_start_index
    )
    return es

def normalize(es):
    left, right = es.channels
    left_power = sum(left.power)
    right_power = sum(right.power)
    right.signal *= (left_power / right_power)
    max_sample = max(max(left.signal), max(right.signal))
    left.signal = left.signal * (32768.0 / max(left.signal))
    right.signal = right.signal * (32768.0 / max(right.signal))
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


@stage()
def normalize_samples(es):
    max_val = max([max(c.signal) for c in es.channels])
    for c in es.channels:
        c.signal *= (max_val / max(c.signal)).astype(es.np_format)
    return es
