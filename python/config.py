import alsaaudio as aa
import numpy as np

CHANNELS = 2
FORMAT = aa.PCM_FORMAT_S16_LE
PERIOD_SIZE = 1000
RATE = 192000

def format_size(format):
    return {
        aa.PCM_FORMAT_S16_LE : 2,
        aa.PCM_FORMAT_S24_LE: 3,
        aa.PCM_FORMAT_FLOAT_LE: 4
    }.get(format)

def format_np(format):
    return {
        aa.PCM_FORMAT_S16_LE: np.int16,
        aa.PCM_FORMAT_FLOAT_LE: np.float32
    }.get(format)

class Settings(object):

    def __init__(self, input_device=None, output_device=None):
        self.input = input_device
        self.output = output_device

    def must_resample(self):
        return self.input.rate != self.output.rate


class Device(object):

    def __init__(self, name, rate=RATE, channels=CHANNELS, format=FORMAT, period_size=PERIOD_SIZE):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size
