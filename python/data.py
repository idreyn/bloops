from __future__ import division

import struct
import numpy as np

import math
import wave

from config import Settings

def require_frames(fn):
	def do_let(self, *args):
		if not self.frames:
			raise Exception("Need frames")
		else:
			return fn(self, *args)
	return do_let

def play_frames(audio, frames, rate_mutliplier=1):
	stream = audio.open(
		format=frames.settings.pa_format,
		channels=frames.settings.channels,
		rate=int(frames.settings.rate * rate_mutliplier),
		frames_per_buffer=frames.settings.chunk,
		output=True
	)
	for f in frames:
		stream.write(f)
	stream.close()

def chunks(l, n):
	res = []
	for i in xrange(0, len(l), n):
		res.append(l[i:i+n])
	return res

class AudioData(object):
	def __init__(self, settings, frames):
		self.settings = settings
		self.frames = frames

	@staticmethod
	def read_wave(settings, file):
		res = []
		wf = wave.open(file,'rb')
		params = wf.getparams()
		if not params[0:3] == (
			settings.channels,
			settings.width,
			settings.rate
		):
			raise Exception("Opening file using incompatible Settings")
		data = wf.readframes(settings.chunk)
		while len(data):
			res.append(data)
			data = wf.readframes(settings.chunk)
		return AudioData(settings, res)

	@staticmethod
	def from_array(settings, arr):
		return AudioData(
			settings,
			chunks(
				np.transpose(arr)
					.flatten()
					.astype(settings.np_format)
					.tostring(),
				settings.chunk * settings.channels * settings.width
			)
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
		array = np.fromstring(
			''.join(self.frames),
			dtype=self.settings.np_format
		)
		return np.transpose(
			np.reshape(
				array,
				(len(array) / channels, channels)
			)
		)