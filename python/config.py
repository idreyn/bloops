import sounddevice as sd
import numpy as np

NP_FORMAT = np.int16
CHANNELS = 2
CHUNK = 0

DEFAULT_SAMPLE_RATE = 'default_samplerate'
MAX_INPUT_CHANNELS = 'max_input_channels'
MAX_OUTPUT_CHANNELS = 'max_output_channels'

def get_channel_string(is_input):
	return MAX_INPUT_CHANNELS if is_input else MAX_OUTPUT_CHANNELS

class Settings(object):
	def __init__(self, input_device=None, output_device=None, 
			np_format=NP_FORMAT, chunk=CHUNK):
		self.input = input_device
		self.output = output_device
		self.np_format = np_format
		self.chunk = chunk

	def must_resample(self):
		return self.input.rate != self.output.rate

class Device(object):
	def __init__(self, index, info, is_input=True):
		self.index = index
		self.info = info
		self.is_input = is_input
		self.name = info.get("name")
		self.channels = int(info.get(get_channel_string(is_input)))
		self.rate = int(info.get(DEFAULT_SAMPLE_RATE))

def choose_device(is_input):
	max_dsr = 0
	best_index= -1
	best = None
	channel_string = get_channel_string(is_input)
	for i, info in enumerate(sd.query_devices()):
		if int(info.get(channel_string)) == CHANNELS:
			if info.get(DEFAULT_SAMPLE_RATE) > max_dsr:
				max_dsr = info.get(DEFAULT_SAMPLE_RATE)
				best_index = i
				best = info
	if best is None:
		raise Exception("Failed to find appropriate device")
	return Device(best_index, best, is_input)

def choose_input():
	return choose_device(True)

def choose_output():
	return choose_device(False)
