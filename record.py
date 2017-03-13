import time
import numpy as np

from data import periods_to_array
from stream import Stream
from samplebuffer import SampleBuffer

class Recorder(object):
    def __init__(self, stream):
        self.okay = True
        self.stream = stream

    def get_recording(self, length_secs):
        device = self.stream.device
        start_time = time.time()
        self.buffer = SampleBuffer(
            device.channels,
            length_secs * device.rate / device.period_size
        )
        while time.time() - start_time < length_secs:
            self.buffer.put(self.stream.read_array(0.0001))
        return self.buffer.get_samples(
            length_secs * device.rate,
            start_time
        )