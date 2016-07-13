from multiprocessing import Queue

import pyaudio
import numpy as np

from scipy.signal import chirp
from scipy.fftpack import *

from frames import Frames
from config import *

class Pulse(object):
	def __init__(self,us_duration,square=False):
		self.us_duration = us_duration
		self.square = square
		self.__t_axis = None
		self.__rendered = None

	def t_axis(self):
		if not self.__t_axis is None:
			return self.__t_axis
		self.__t_axis = np.linspace(0,1e-6 * self.us_duration,1e-6 * self.us_duration * RATE)
		return self.__t_axis

	def render(self):
		if not self.__rendered is None:
			return self.__rendered
		r = self._render()
		if self.square:
			r[r > 0] = 1
			r[r < 0] = -1
		self.__rendered = r
		return r

	def _render(self):
		raise Exception("Pulse should not be instantiated directly")

class Tone(Pulse):
	def __init__(self,frequency,us_duration,square=False):
		super(Tone,self).__init__(us_duration,square)
		self.frequency = frequency
		self.us_duration = us_duration

	def _render(self):
		return np.cos(2 * np.pi * self.frequency * self.t_axis())

class Chirp(Pulse):
	def __init__(self,f0,f1,us_duration,method,square=False):
		super(Chirp,self).__init__(us_duration,square)
		self.f0 = f0
		self.f1 = f1
		self.us_duration = us_duration
		self.method = method

	def _render(self):
		times = self.t_axis()
		t1 = times[-1]
		return chirp(
			t=self.t_axis(),
			f0=self.f0,
			f1=self.f1,
			t1=t1,
			method=self.method
		)

class Click(Pulse):
	def __init__(self,us_duration,f_low,f_high):
		super(Click,self).__init__(us_duration)
		self.f_low = f_low
		self.f_high = f_high

	def _render(self):
		res = np.empty(len(self.t_axis()))
		for f in xrange(self.f_low,self.f_high,100):
			res = res + np.cos(2 * np.pi * f * self.t_axis())
		return res
		
class Emitter(object):
	def __init__(self, settings):
		self.audio = audio
		def do_stream(a,b,c,d):
			self.do_stream(a,b,c,d)
		self.stream = audio.open(
			output_device_index=settings.output_device_index,
			format=settings.format,
			channels=settings.channels,
			rate=settings.rate,
			frames_per_buffer=settings.chunk,
			output=True,
		)
		self.clear_queue()

	def clear_queue(self):
		self.queue = Queue()

	def play(self,data):
		frames = Frames.from_array(data)
		self.clear_queue()
		for f in frames:
			self.queue.put(f)

	def do_stream(self,id,fc,ta,s):
		if not self.queue.empty():
			return (
				self.queue.get(True),
				pyaudio.paContinue
			)

	def start(self):
		self.playing = True
		self.stream.start_stream()

	def stop(self):
		self.playing = False
		self.stream.stop_stream()