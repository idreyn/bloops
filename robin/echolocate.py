from __future__ import division

import numpy as np
from scikits.samplerate import resample
import resampy

from config import DAC, ULTRAMICS
from gpio import emitter_enable
from pulse import Silence
from save import save_file
from stream import Stream
from util import zero_pad, zero_pad_to_multiple, bandpass

import time


class Echolocation(object):

    def __init__(self, pulse, slowdown, device,
                 us_record_time=1e5, us_silence_before=1e4):
        self.pulse = pulse
        self.slowdown = slowdown
        self.device = device
        self.us_silence_before = us_silence_before
        self.us_record_time = us_record_time


def simple_loop(ex, audio, pipeline=None):
    assert isinstance(ex, Echolocation)
    rendered = zero_pad(ex.pulse.render(DAC), 50, 50)
    with audio as (record, emit):
        with emitter_enable:
            if ex.us_silence_before:
                emit.write_array(Silence(ex.us_silence_before).render(DAC))
            emit.write_array(rendered)
            sample = record.read_array(1e-6 * ex.us_record_time)
    if pipeline:
        sample = pipeline.run(ex, sample)
    playback = Stream(DAC, False, False)
    chunks = []
    for chunk in np.split(zero_pad_to_multiple(sample, ex.slowdown), ex.slowdown):
        t0 = time.time()
        chunk = resample(chunk, ex.slowdown, 'sinc_fastest')
        playback.write_array(chunk)
        print "chunk in", time.time() - t0, len(chunk), len(chunk) / ULTRAMICS.rate
        time.sleep(0.04)
        chunks.append(chunk)
    playback.close()
    resampled = np.concatenate(chunks)
    print resampled.shape
    save_file(ULTRAMICS, resampled, str(ex.pulse) + "__resampled")
    save_file(ULTRAMICS, rendered, str(ex.pulse) + "__pulse")
    save_file(ULTRAMICS, sample, str(ex.pulse))
