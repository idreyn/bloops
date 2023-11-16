import signal, sys
import math

import numpy as np
from scipy.signal import iirnotch, lfilter, butter


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
