import pyaudio
import time
from queue import Queue

from config import *

class Recorder(object):
	def __init__(self,audio):
		def stream_cb(*args):
			return self.do_stream(*args)
		self.clear_queue()
		self.stream = audio.open(
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			input=True,
			frames_per_buffer=CHUNK,
			stream_callback=stream_cb
		)
		self.stream.start_stream()

	def record(self,seconds):
		self.clear_queue()
		for i in xrange(0, int(RATE / CHUNK * seconds)):
			yield self.queue.get(True)

	def clear_queue(self):
		self.queue = Queue()

	def do_stream(self,data,fc,time,flags):
		self.queue.put(data)
		return (None,pyaudio.paContinue)

