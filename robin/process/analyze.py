import random
import peakutils

import numpy as np


def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, "valid")
    return sma


def find_signal_start(
    left,
    right,
    left_silence=None,
    right_silence=None,
    silence_boundary_index=None,
    cutoff_index=None,
    window=100,
    factor=10,
):
    if cutoff_index:
        left = left[0:cutoff_index]
        right = right[0:cutoff_index]
    left_rms = np.std(left)
    right_rms = np.std(right)
    if (
        left_silence is None
        and right_silence is None
        and silence_boundary_index is None
    ):
        raise Exception("Need either silence samples or boundary index")
    else:
        if silence_boundary_index:
            left_silence = left[0:silence_boundary_index]
            right_silence = right[0:silence_boundary_index]
            left = left[silence_boundary_index:]
            right = right[silence_boundary_index:]
    left_silence_pwr = sum(left_silence**2) / len(left_silence)
    right_silence_pwr = sum(right_silence**2) / len(right_silence)
    left = moving_average(left**2, window)
    right = moving_average(right**2, window)
    left_start_index = np.argmax(left > (factor * left_silence_pwr))
    right_start_index = np.argmax(right > (factor * right_silence_pwr))
    return left_start_index, right_start_index


def align(left, right, lsi, rsi):
    offset = lsi - rsi
    if offset < 0:
        offset = 0 - offset
        first_is_left = True
        first = left
        last = right
    else:
        first_is_left = False
        first = right
        last = left
    if offset > 0:
        first = first[:-offset]
        last = last[offset:]
    return first if first_is_left else last, last if first_is_left else first
