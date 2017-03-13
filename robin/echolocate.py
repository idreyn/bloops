from scipy.signal import *

from audio import *
from config import *
from gpio import *
from process import *
from pulse import *
from save import *

dac = AudioDevice('dac', 192000)
ultramics = AudioDevice('ultramics', 192000)

audio = Audio(ultramics, dac)

def simple_loop(pulse_source, slowdown=20):
	pulse = pulse_source(dac)
	print "emit!", str(pulse)
	with audio as (record, emit):
		with emitter_enable:
			emit.write_array(Silence(dac, 1e4).render())
			emit.write_array(pulse_source(dac).render())
			rec = bandpass(record.read_array(0.1), 1e4, 9e4, dac.rate)
	resampled = resample(rec, slowdown * len(rec))
	playback = Stream(dac, False, True)
	playback.write_array(resampled)
	playback.close()
	save_file(ultramics, resampled, str(pulse) + "__resampled")
	save_file(ultramics, rec, str(pulse))
