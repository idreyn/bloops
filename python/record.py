import time
import math
from queue import Queue

import pyaudio
import numpy as np

from config import *
from util import *
from frames import *

class Recorder(object):
	def __init__(self, audio, settings, device_index=None):
		def stream_cb(*args):
			return self.do_stream(*args)
		self.clear_queue()
		self.stream = audio.open(
			input_device_index=device_index,
			format=settings.pa_format,
			channels=settings.channels,
			rate=settings.rate,
			input=True,
			frames_per_buffer=settings.chunk,
			stream_callback=stream_cb
		)
		self.settings = settings
		self.start()

	def record(self,seconds):
		self.clear_queue()
		for i in xrange(0, int(settings.rate / settings.chunk * seconds)):
			yield i, self.queue.get(True)

	def clear_queue(self):
		self.queue = Queue()

	def do_stream(self, data, *rest):
		self.queue.put(data)
		return (None, pyaudio.paContinue)

	def start(self):
		self.stream.start_stream()
		self.listening = True

	def stop(self):
		self.stream.stop_stream()
		self.listening = False


