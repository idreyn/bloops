import pyaudio
import time

import numpy as np

from emit import *
from record import *
from process import *
from util import *

class Environment(object):
	def __init__(self):
		self.us_pingback = np.inf

	def obstacle_distance(self):
		return (self.us_pingback / 2) * SPEED_OF_SOUND

	def suggest_us_pulse_duration(self):
		if self.us_pingback == np.inf:
			return 10 * 1000
		else:
			return round_to_nearest(self.us_pingback / 4,1000)

	def estimate_us_record_duration(self,pulse):
		return 2 * self.us_pingback + pulse.duration

class Robin(object):
	def __init__(self):
		self.audio = pyaudio.PyAudio()
		self.env = Environment()
		self.rec = Recorder(self.audio)
		self.emit = Emitter(self.audio)
		self.outputs_queue = Queue()

	def start_listening(self):
		self.rec.start()

	def stop_listening(self):
		self.rec.stop()

	def emit_record(pulse):
		if not self.rec.listening:
			self.rec.start()
		t0 = self.emit.play_pulse(pulse)
		left_channel = []
		right_channel = []
		for (data,fc,time,flags) in self.rec.record(self.env.estimate_us_record_duration())
		sample = EnvironmentSample([
			ChannelSample(left_channel), ChannelSample(right_channel)
		])
		output, us_pingback = sample.process()
		self.env.us_pingback = us_pingback
		
if __name__ == '__main__':
	robin = Robin()
