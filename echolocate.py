from scipy.signal import *

from audio import *
from config import *
from gpio import *
from process import *
from pulse import *
from save import *

audio = Audio(ULTRAMICS, DAC)

def simple_loop(pulse_source, slowdown=20):
	pulse = pulse_source(DAC)
	print "emit!", str(pulse)
	with audio as (record, emit):
		with emitter_enable:
                        emit.write_array(Silence(DAC, 1e4).render())
                        emit.write_array(Tone(DAC, 4e4, 1e3).render())
			emit.write_array(Silence(DAC, 1e4).render())
			emit.write_array(pulse_source(DAC).render())
			rec = record.read_array(0.1)
	resampled = resample(rec, slowdown * len(rec))
	# playback = Stream(dac, False, True)
	# playback.write_array(resampled)
	# playback.close()
	# save_file(ULTRAMICS, resampled, str(pulse) + "__resampled")
	save_file(ULTRAMICS, rec, str(pulse))
