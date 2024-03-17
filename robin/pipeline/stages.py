import numpy as np
import scipy.signal

import robin.util as util

from robin.config import Config
from robin.noisereduce import noise_reduce, NoiseReduceSettings
from robin.pipeline.sample import EnvironmentSample
from robin.logger import log


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
        def func_wrapper(es, config):
            if not type(es) is EnvironmentSample:  # noqa: E714
                raise Exception(
                    "Stage %s was not passed an EnvironmentSample"
                    % (stage_func.__name__)
                )
            if not es.passed_stages(require):
                raise Exception(
                    (
                        "Cannot run pipeline stage %s without first"
                        + " running its required stages."
                    )
                    % (stage_func.__name__)
                )
            if len(forbid) > 0 and es.passed_stages(forbid):
                raise Exception(
                    (
                        "Cannot run pipeline stage %s because a forbidden stage"
                        + " has already been applied."
                    )
                    % (stage_func.__name__)
                )
            es = stage_func(es, config)
            if not type(es) is EnvironmentSample:  # noqa: E714
                raise Exception(
                    "Stage %s did not return an EnvironmentSample"
                    % (stage_func.__name__)
                )
            es.pass_stage(stage_func.__stage__)
            return es

        setattr(stage_func, "__stage__", func_wrapper)
        return func_wrapper

    return decorator


@stage()
def stats(es, *rest):
    for i, c in enumerate(es.channels):
        c.max_val = max(c.signal)
        c.argmax = np.argmax(c.signal)
        c.avg_power = sum(c.signal**2) / len(c.signal)
        log(
            "channel %s: max %s argmax %s avg_power %s"
            % (i, c.max_val, c.argmax, c.avg_power)
        )
    return es


@stage()
def bandpass(es, *rest):
    for c in es.channels:
        log(f"Bandpassing {es.hz_band} {es.rate}")
        c.signal = util.bandpass(c.signal, es.hz_band[0], es.hz_band[1], es.rate)
    return es


@stage()
def skeri_notch(es, *rest):
    for c in es.channels:
        for _ in range(3):
            c.signal = util.notch(
                c.signal,
                32750,
                es.rate,
            )
            c.signal = util.notch(
                c.signal,
                53250,
                es.rate,
            )
    return es


@stage()
def self_notch(es, *rest):
    for c in es.channels:
        for khz in range(1, 5):
            for _ in range(3):
                c.signal = util.notch(
                    c.signal,
                    1000 * khz,
                    es.rate,
                )
    return es


@stage()
def detrend(es, *rest):
    for c in es.channels:
        c.signal = scipy.signal.detrend(c.signal, type="constant")
    return es


@stage(require=[bandpass])
def find_pulse_start_index(es, *rest):
    left, right = es.channels
    lps, rps = util.find_signal_start(
        left=left.signal,
        right=right.signal,
        left_silence=left.silence,
        right_silence=right.silence,
        cutoff_index=int(
            1e-3 * (es.ms_silence_before + es.ms_pulse_duration) / es.rate
        ),
    )
    left.pulse_start_offset = lps
    right.pulse_start_offset = rps
    return es


@stage(require=[find_pulse_start_index])
def remove_leading_silence(es, *rest):
    left, right = es.channels
    start_index = min(left.pulse_start_offset, right.pulse_start_offset)
    log(f"Removing leading silence: {1000 * start_index / es.rate}ms")
    left.signal = left.signal[start_index:]
    right.signal = right.signal[start_index:]
    return es


@stage(require=[remove_leading_silence])
def attunate_emission(es, config: Config):
    if config.current.echolocation.emission_gain < 1:
        through_index = int(es.rate * 1e-3 * es.ms_pulse_duration)
        for channel in es.channels:
            channel.signal[0:through_index] = 0
    return es


@stage()
def normalize(es):
    left, right = es.channels
    max_value = 32768  # noqa: F841
    max_sample = max(max(left.signal), max(right.signal))
    left.signal = left.signal * (32768.0 / max_sample)
    right.signal = right.signal * (32768.0 / max_sample)
    return es


@stage(require=[detrend], forbid=[normalize])
def noisereduce(es):
    for c in es.channels:
        c.signal = noise_reduce(
            c.signal.astype(np.float64),
            c.silence.astype(np.float64),
            NoiseReduceSettings(),
        )
    return es


@stage()
def normalize_samples(es):
    max_val = max([max(c.signal) for c in es.channels])
    for c in es.channels:
        c.signal *= (max_val / max(c.signal)).astype(es.np_format)
    return es
