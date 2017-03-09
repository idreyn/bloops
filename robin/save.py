import time
import datetime as dt

from scikits.audiolab import Sndfile, Format

def now_stamp():
	t0 = time.time()
	return dt.datetime.fromtimestamp(t0).strftime('%Y-%m-%d-%H-%M-%S')

def save_file(device, sound, name_append=None, prefix="../recordings/"):
	file = Sndfile(prefix + now_stamp() + (
		"__" + name_append if name_append else ""
	) + ".wav", 'w', Format('wav', 'pcm16'), device.channels, device.rate)
	file.write_frames((1.0 / 32678) * sound)
	file.close()