from __future__ import division

import struct
import numpy as np

import math
import wave

from config import Settings
from util import log, ceil_to_nearest

def require_frames(fn):
	def do_let(self, *args):
		if not self.frames:
			raise Exception("Need frames")
		else:
			return fn(self, *args)
	return do_let

def pad_to_size(sample,length):
	zeroes = np.repeat(0,length - len(sample))
	return np.concatenate((sample,zeroes))

def play_array(audio,data,rate_mutliplier=1,channels=None):
	data = pad_to_size(data,CHUNK * (1 + len(data) / CHUNK))
	frames = array_to_frames(data)
	play_frames(audio,frames,rate_mutliplier,channels=channels)

def play_frames(audio,frames,rate_mutliplier=1,channels=None):
	stream = audio.open(
		format=FORMAT,
		channels=channels or CHANNELS,
		rate=int(RATE * rate_mutliplier),
		frames_per_buffer=CHUNK,
		# output_device_index=OUTPUT_DEVICE_INDEX,
		output=True
	)
	for f in frames:
		stream.write(f)
	stream.close()

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]
	
def normalize(arr):
	if len(arr.shape) == 1:
		nx = np.empty((1,len(arr)))
		nx[0] = arr
		return nx
	return arr

class Frames(object):
	def __init__(self,settings,frames):
		self.settings = settings
		self.frames = frames

	@staticmethod
	def read_wave(settings, file):
		res = []
		wf = wave.open(file,'rb')
		data = wf.readframes(settings.chunk)
		while data != '':
			res.append(data)
			data = wf.readframes(settings.chunk)
		res.append(data)
		return Frames(settings, ''.join(res))

	@staticmethod
	def from_array(settings, arr):
		return Frames(
			settings,
			np.transpose(arr)
				.flatten()
				.astype(settings.np_format)
				.tostring()
		)

	@require_frames
	def write_wave(self, filename):
		file = open(filename,'w')
		for f in self.frames:
			file.write(f)
		file.close()

	@require_frames
	def to_array(self):
		width = self.settings.chunk * self.settings.channels
		channels = self.settings.channels
		array = np.fromstring(self.frames, dtype=self.settings.np_format)
		return np.transpose(
			np.reshape(
				array,
				(len(array) / channels, channels)
			)
		)