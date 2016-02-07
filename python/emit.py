import numpy as np

from config import *

class Pulse(object):
	def __init__(self,start,end,us_duration):
		self.us_duration = duration

	def t_axis():
		return np.linspace(0,us_duration,1e-6 * RATE * self.us_duration)

	def render():
		raise Exception("Pulse should not be instantiated directly")

class Tone(Pulse):
	def __init__(self,frequency,us_duration):
		self.frequency = frequency

	def render(self):
		return np.cos((0.5 / np.pi) * self.frequency * self.t_axis())

class Chirp(Pulse):
	def __init__(self,f0,f1,us_duration,method):
		self.f0 = f0
		self.f1 = f1
		self.us_duration
		self.method = method

	def render(self):
		return chirp(
			t=self.t_axis(),
			f0=self.f0,
			f1=self.f1,
			t1=self.us_duration,
			method=self.method
		)

class Emitter(object):
	def __init__(self,audio):
		self.audio = self.audio
		self.stream = audio.open(
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			output=True,
			frames_per_buffer=CHUNK,
			stream_callback=stream_cb
		)
		self.start()

	def start(self):
		self.playing = True
		self.stream.start_stream()

	def stop(self):
		self.playing = False
		self.stream.stop_stream()

	@memoize
	def null_chunk(self):
		return np.zeros(CHUNK_SIZE)
