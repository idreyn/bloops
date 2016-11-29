import alsaaudio as aa

CHANNELS = 2
FORMAT = aa.PCM_FORMAT_S16_LE
PERIODSIZE = 1000
RATE = 120000

MIN_OUTPUT_RATE = None
MIN_INPUT_RATE = None

DEFAULT_SAMPLE_RATE = 'default_samplerate'
MAX_INPUT_CHANNELS = 'max_input_channels'
MAX_OUTPUT_CHANNELS = 'max_output_channels'

def get_channel_string(is_input):
	return MAX_INPUT_CHANNELS if is_input else MAX_OUTPUT_CHANNELS

class Settings(object):
    def __init__(self, input_device=None, output_device=None):
        self.input = input_device
	self.output = output_device

    def must_resample(self):
	return self.input.rate != self.output.rate

class Device(object):
    def __init__(self, name, rate=RATE, channels=CHANNELS, format=FORMAT, periodsize=PERIODSIZE):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.periodsize = periodsize

"""
def choose_device(is_input):
	max_dsr = (MIN_INPUT_RATE or 0) if is_input else (MIN_OUTPUT_RATE or 0)
	best_index= -1
	best = None
	channel_string = get_channel_string(is_input)
	for i, info in enumerate(sd.query_devices()):
		print info
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
"""
