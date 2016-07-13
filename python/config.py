import pyaudio
import numpy as np

PA_FORMAT = pyaudio.paFloat32
NP_FORMAT = np.float32
CHANNELS = 2
RATE = 192000
CHUNK = 1024
OUTPUT_DEVICE_INDEX = 0

FORMATS = [
	(pyaudio.paInt16, np.int16, 2),
	(pyaudio.paInt32, np.int32, 4),
	(pyaudio.paFloat32, np.float32, 4),
]

class Settings(object):
	def __init__(
		self,
		pa_format=None,
		np_format=None,
		channels=CHANNELS,
		rate=RATE,
		chunk=CHUNK,
		output_device_index=OUTPUT_DEVICE_INDEX
	):
		self.channels = channels
		self.rate = rate
		self.chunk = chunk
		self.output_device_index = output_device_index
		one_format = (pa_format and not np_format) \
			or (np_format and not pa_format)
		if not one_format:
			raise Exception(
				"Please provide Settings with either pa_format or np_format, "
				"but not both!"
			)
		search_index = 0 if pa_format else 1
		fmts = [
			f for f in FORMATS
			if f[search_index] is (pa_format or np_format)
		]
		if not len(fmts):
			raise Exception("Invalid format supplied")
		self.pa_format = fmts[0][0]
		self.np_format = fmts[0][1]
		self.width = fmts[0][2]
		
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
