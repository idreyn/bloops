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


import numpy as np


def split_on_silence(signal, threshold_db, filter_window_length):
    """
    Split a signal into segments based on silence, automatically normalizing and re-normalizing the signal.

    Parameters:
    signal (ndarray): Input signal array.
    threshold_db (float): Silence threshold in dB.
    hyst_samples (int, optional): Number of samples for hysteresis smoothing. Defaults to 10.
    filter_window_length (int, optional): Moving average filter window length. Defaults to 5.

    Returns:
    list of ndarray: List of segments of the signal, split on silent parts, in the original data type.
    """
    original_dtype = signal.dtype

    # Normalization factor based on the maximum value of the input dtype
    dtype_max = (
        np.iinfo(original_dtype).max
        if np.issubdtype(original_dtype, np.integer)
        else 1.0
    )

    # Convert to float32 and normalize
    normalized_signal = signal.astype(np.float32) / dtype_max

    # Square each element to get signal power timeseries
    power_signal = np.square(normalized_signal)

    # Compute threshold power
    threshold_power = np.max(power_signal) * 10 ** (threshold_db / 10)

    # Apply low-pass filtering on the power signal
    window = np.ones(filter_window_length) / filter_window_length
    filtered_power_signal = np.convolve(power_signal, window, mode="same")

    # Map each element to 0 or 1 based on threshold
    thresholded_signal = (filtered_power_signal > threshold_power).astype(int)

    # Find ranges where the array is 1 (non-silent segments) and create arrays
    non_silent_segments = []
    start = None
    for i, value in enumerate(thresholded_signal):
        if value == 1 and start is None:
            start = i
        elif value == 0 and start is not None:
            segment = normalized_signal[start:i] * dtype_max
            non_silent_segments.append(segment.astype(original_dtype))
            start = None
    if start is not None:
        segment = normalized_signal[start:] * dtype_max
        non_silent_segments.append(segment.astype(original_dtype))

    return non_silent_segments
