import pyaudio
import time
import math
from queue import Queue

import numpy as np

from config import *
from util import *
from wav import *

class Recorder(object):
	def __init__(self,audio,input_device_index=None):
		def stream_cb(*args):
			return self.do_stream(*args)
		if input_device_index is None:
			input_device_index = choose_microphone(audio).get('index')
		log("Starting Recorder with device " + str(input_device_index))
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

	def chunks_in_seconds(self,seconds):
		return int(RATE / CHUNK * seconds)

	def record(self,seconds):
		self.clear_queue()
		chunks = self.chunks_in_seconds(seconds)
		for data in xrange(0,chunks):
			res, _, _, _ = self.queue.get(True)
			yield res

	def record_to_arr(self,seconds=None,microseconds=None):
		if seconds is None:
			if microseconds is None:
				raise Error("Unspecified record duration")
			else:
				seconds = 1e-6 * microseconds
		data = []
		for i, nxt in enumerate(self.record(seconds)):
			data.append(nxt)
		data = ''.join(data)
		return np.reshape(
			np.fromstring(data,dtype=NP_FORMAT),
			(CHUNK * (i+1),2)
		)
		
	def clear_queue(self):
		self.queue = Queue()

	def do_stream(self,data,fc,time,flags):
		self.queue.put((data,fc,time,flags))
		return (None,pyaudio.paContinue)

	def start(self):
		self.stream.start_stream()
		self.listening = True

	def stop(self):
		self.stream.stop_stream()
		self.listening = False

