from scipy.signal import *

from audio import *
from config import *
from gpio import *
from process import *
from pulse import *
from save import *


class Echolocation(object):

    def __init__(self, pulse, slowdown,
                 us_silence_before=1e4, us_record_time=1e5):
        self.pulse = pulse
        self.slowdown = slowdown
        self.us_silence_before = us_silence_before
        self.us_record_time = us_record_time


def simple_loop(ex, audio, pipeline=None):
	assert type(ex) is Echolocation
    with audio as (record, emit):
        with emitter_enable:
        	if ex.us_silence_before:
            	emit.write_array(Silence(ex.us_silence_before).render(dac))
            emit.write_array(ex.pulse.render(dac))
            sample = record.read_array(1e-6 * ex.us_record_time)
    if pipeline:
    	sample = pipeline.run(sample)
    resampled = resample(rec, ex.slowdown * len(sample))
    playback = Stream(dac, False, True)
    playback.write_array(resampled)
    playback.close()
    save_file(ultramics, resampled, str(pulse) + "__resampled")
    save_file(ultramics, rec, str(pulse))
