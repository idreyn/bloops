import signal, sys
import math
import numpy as np
from scipy.signal import iirnotch, lfilter, butter


def chunks(l, n):
    res = []
    for i in range(0, len(l), n):
        res.append(l[i : i + n])
    return res


def pad(array, length, pad):
    if len(array) == length:
        return array
    extra = [pad] * (length - len(array))
    return array + extra


def array_to_periods(array, device):
    return chunks(
        array.flatten().astype(device.np_format).tostring(), device.period_bytes()
    )


def periods_to_array(frames, device):
    channels = device.channels
    array = np.frombuffer(b"".join(frames), dtype=device.np_format)
    return np.reshape(array, (len(array) // channels, channels))


def to_db(val):
    return 10 * np.log10((0.00000001 + np.abs(val)) ** 2)


def from_db(val):
    return np.power(10, (1.0 / 20) * val)


def bandpass_coefficients(lowcut, highcut, fs, order=1):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="bandpass")
    return b, a


def bandpass(data, low, high, rate):
    bpf = bandpass_coefficients(low, high, rate)
    return lfilter(bpf[0], bpf[1], data)


def notch(signal, f0, rate, Q=30):
    b, a = iirnotch(f0, Q, rate)
    return lfilter(b, a, signal)


def t_axis(sample, rate):
    return np.linspace(0, len(sample) / rate, len(sample))


def zero_pad(sample, left_length=0, right_length=0):
    return np.pad(sample, ((left_length, right_length), (0, 0)), mode="constant")


def zero_pad_to_multiple(sample, factor):
    next_multiple = factor * int(math.ceil(len(sample) / factor))
    return zero_pad(sample, right_length=(next_multiple - len(sample)))


def zero_pad_power_of_two(sample):
    next_power = 2 ** math.ceil(math.log(len(sample), 2))
    return zero_pad(sample, right_length=(next_power - len(sample)))


def handle_close():
    def signal_handler(signal, frame):
        kill_app()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)


def get_ip_address():
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "unavailable"


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


def remove_leading_silence(signal, threshold_db):
    """
    Slice off silence from the beginning of a signal array and return the trimmed signal.

    Parameters:
    signal (ndarray): Input signal array.
    threshold_db (float): Silence threshold in dB.

    Returns:
    ndarray: The trimmed signal, starting from the first non-silent part.
    """
    original_dtype = signal.dtype
    dtype_max = (
        np.iinfo(original_dtype).max
        if np.issubdtype(original_dtype, np.integer)
        else 1.0
    )

    # Convert to float32 and normalize
    normalized_signal = signal.astype(np.float32) / dtype_max

    # Compute threshold power
    threshold_power = 10 ** (threshold_db / 10)

    # Square each element to get signal power timeseries
    power_signal = np.square(normalized_signal)

    # Find the start of the first non-silent segment
    non_silent_start = np.argmax(power_signal > threshold_power)

    # Slice the signal from the non-silent start
    trimmed_signal = normalized_signal[non_silent_start:] * dtype_max

    return trimmed_signal.astype(original_dtype)


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
