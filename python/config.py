import sounddevice as sd
import numpy as np

NP_FORMAT = np.float32
CHANNELS = 2
RATE = 192000
CHUNK = 0

DEFAULT_SAMPLE_RATE = 'default_samplerate'
MAX_INPUT_CHANNELS = 'max_input_channels'
MAX_OUTPUT_CHANNELS = 'max_output_channels'

class Settings(object):
	def __init__(self, np_format=None, device=None,
			channels=None, rate=None, chunk=None):
		assert not device or type(device) is Device
		dev_rate = int(device.info[DEFAULT_SAMPLE_RATE]) if device else None
		dev_channels = int(device.info[MAX_INPUT_CHANNELS]) if device else None
		self.channels = channels or dev_channels or CHANNELS
		self.rate = rate or dev_rate or RATE
		self.chunk = chunk or CHUNK
		self.np_format = np_format

class Device(object):
	def __init__(self, index, info):
		self.index = index
		self.info = info

def choose_device(input):
	max_dsr = 0
	best_index= -1
	best = None
	channelString = MAX_INPUT_CHANNELS if input else MAX_OUTPUT_CHANNELS
	for i, info in enumerate(sd.query_devices()):
		if info.get(channelString) == 2:
			if info.get(DEFAULT_SAMPLE_RATE) > max_dsr:
				max_dsr = info.get(DEFAULT_SAMPLE_RATE)
				best_index = i
				best = info
	return Device(best_index, best)

def choose_input():
	return choose_device(True)

def choose_output():
	return choose_device(False)