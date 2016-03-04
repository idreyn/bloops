import pyaudio
import time
import math
from queue import Queue

import numpy as np

from config import *
from util import *
from frames import *

class Recorder(object):
	def __init__(self,audio,input_device_index=None):
		def stream_cb(*args):
			return self.do_stream(*args)
		self.clear_queue()
		self.stream = audio.open(
			input_device_index=input_device_index,
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			input=True,
			frames_per_buffer=CHUNK,
			stream_callback=stream_cb
		)
		self.start()

	def record(self,seconds):
		self.clear_queue()
		for i in xrange(0, int(RATE / CHUNK * seconds)):
			yield i, self.queue.get(True)

	def clear_queue(self):
		self.queue = Queue()

	def do_stream(self,data,fc,time,flags):
		self.queue.put(data)
		return (None,pyaudio.paContinue)

	def start(self):
		self.stream.start_stream()
		self.listening = True

	def stop(self):
		self.stream.stop_stream()
		self.listening = False


