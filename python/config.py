import pyaudio
import numpy as np

PA_FORMAT = pyaudio.paFloat32
NP_FORMAT = np.float32
CHANNELS = 2
RATE = 192000
CHUNK = 1024
OUTPUT_DEVICE_INDEX = 0

class Settings(object):
	def __init__(
		self,
		pa_format=PA_FORMAT,
		np_format=NP_FORMAT,
		channels=CHANNELS,
		rate=RATE,
		chunk=CHUNK,
		output_device_index=OUTPUT_DEVICE_INDEX
	):
		self.pa_format = pa_format
		self.np_format = np_format
		self.channels = channels
		self.rate = rate
		self.chunk = chunk
		self.output_device_index = output_device_index

def enumerate_devices(audio, debug=False):
	info = audio.get_host_api_info_by_index(0)
	for i in xrange(info.get('deviceCount')):
		info = audio.get_device_info_by_host_api_device_index(0,i)
		if debug:
			print info
		yield i, info

def choose_input(audio):
	max_dsr = 0
	best = None
	for i, info in enumerate_devices(audio):
		if info.get('maxInputChannels') == 2:
			if info.get('defaultSampleRate') > max_dsr:
				max_dsr = info.get('defaultSampleRate')
				best = info
	return best
