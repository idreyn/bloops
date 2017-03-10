import time
import numpy as np
from threading import Thread

from alsaaudio import ALSAAudioError

from data import periods_to_array
from stream import Stream
from samplebuffer import SampleBuffer

def do_record(buffer, stream, handle_failure):
    try:
        while True:
            arr = stream.read_array(0.01)
            buffer.put(arr)
    except ALSAAudioError as e:
        handle_failure()

class Recorder(object):
    def __init__(self, device):
        self.okay = True
        self.device = device
        self.buffer = SampleBuffer(device.channels)
        self.stream = Stream(device, True, True)
        self.record_thread = Thread(
            target=do_record,
            args=(self.buffer, self.stream, self.handle_failure)
        )
        self.record_thread.daemon = True
        self.record_thread.start()

    def get_recording(self, start_time, length_secs):
        return self.buffer.get_samples(
            length_secs * self.device.rate,
            start_time
        )

    def assert_okay(self):
        return self.okay

    def handle_failure(self):
        self.stream.pcm.close()
        self.okay = False

    def close(self):
        self.stream.close()
