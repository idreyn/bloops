import pyaudio
import time
import math

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
		elif input_device_index is False:
			input_device_index = None
		log("Starting Recorder with device " + str(input_device_index))
		self.stream = audio.open(
			input_device_index=input_device_index,
			format=FORMAT,
			channels=CHANNELS,
			rate=RATE,
			input=True,
			frames_per_buffer=CHUNK,
		)
		self.start()

	def chunks_in_seconds(self,seconds):
		return int(RATE / CHUNK * seconds)

	def record(self,seconds=None,microseconds=None):
		if seconds is None:
			if microseconds is None:
				raise Error("Unspecified record duration")
			else:
				seconds = 1e-6 * microseconds
		data = []
		for i in xrange(self.chunks_in_seconds(seconds)):
			data.append(self.stream.read(CHUNK))
		data = ''.join(data)
		return np.reshape(
			np.fromstring(data,dtype=NP_FORMAT),
			(CHUNK * (i+1),CHANNELS)
		)
		
	def start(self):
		self.stream.start_stream()
		self.listening = True

	def stop(self):
		self.stream.stop_stream()
		self.listening = False

