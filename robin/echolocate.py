from scipy.signal import resample

from config import DAC, ULTRAMICS
from gpio import emitter_enable
from pulse import Silence
from save import save_file
from stream import Stream


class Echolocation(object):

    def __init__(self, pulse, slowdown,
                 us_silence_before=1e4, us_record_time=1e5):
        self.pulse = pulse
        self.slowdown = slowdown
        self.us_silence_before = us_silence_before
        self.us_record_time = us_record_time


def simple_loop(ex, audio, pipeline=None):
    assert isinstance(ex, Echolocation)
    with audio as (record, emit):
        with emitter_enable:
            if ex.us_silence_before:
                emit.write_array(Silence(ex.us_silence_before).render(DAC))
            emit.write_array(ex.pulse.render(DAC))
            sample = record.read_array(1e-6 * ex.us_record_time)
    if pipeline:
        sample = pipeline.run(sample)
    resampled = resample(sample, ex.slowdown * len(sample))
    playback = Stream(DAC, False, True)
    playback.write_array(resampled)
    playback.close()
    save_file(ULTRAMICS, resampled, str(ex.pulse) + "__resampled")
    save_file(ULTRAMICS, sample, str(ex.pulse))
