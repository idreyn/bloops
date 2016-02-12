import pyaudio
from queue import Queue
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
	def __init__(self,audio,output_device_index=None):
		self.audio = audio
		def do_stream(a,b,c,d):
			self.do_stream(a,b,c,d)
		self.stream = audio.open(
			output_device_index=output_device_index,
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			output=True,
			frames_per_buffer=CHUNK,
		)
		self.clear_queue()

	def clear_queue(self):
		self.queue = Queue()

	def play(self,frames):
		self.clear_queue()
		for f in frames:
			self.queue.put(f)

	def do_stream(self,id,fc,ta,s):
		if not self.queue.empty():
			return (self.queue.get(True),pyaudio.paContinue)

	def start(self):
		self.playing = True
		self.stream.start_stream()

	def stop(self):
		self.playing = False
		self.stream.stop_stream()