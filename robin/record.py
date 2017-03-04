import numpy as np
from threading import Thread

from data import periods_to_array
from stream import Stream
from samplebuffer import SampleBuffer

def do_record(buffer, stream):
	while True:
		red = stream.read_array(1)
		buffer.put(red)

class Recorder(object):
    def __init__(self, device):
    	self.device = device
        self.buffer = SampleBuffer(device.channels)
        self.stream = Stream(device, True)
        self.record_thread = Thread(
        	target=do_record,
        	args=(self.buffer, self.stream)
        )
        self.record_thread.start()

    def get_recording(self, start_time, length_secs):
    	return self.buffer.get_samples(
    		start_time,
    		length_secs * self.device.rate
    	)