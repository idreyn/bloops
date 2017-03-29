from __future__ import division

from Queue import Queue

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
    rendered = ex.pulse.render(DAC)
    with emitter_enable:
        """
        audio.emit_buffer.clear()
        audio.emit_buffer.put(rendered, flag_removed=True)
        """
        audio.emit_queue.put(rendered)
        t0 = time.time()
        audio.record_buffer.clear()
        record_time = 1e-6 * ex.us_record_time
        time.sleep(record_time)
        sample = audio.record_buffer.get(
            int(record_time * audio.record_stream.device.rate), t0)
    audio.record_stream.pause()
    if pipeline and False:
        sample = pipeline.run(ex, sample)
    chunks = []
    """
    audio.emit_buffer.clear()
    """
    total_chunks = 10
    buffer_first = 0
    buffered = Queue()
    for i, chunk in enumerate(
        np.split(zero_pad_to_multiple(sample, total_chunks), total_chunks)
    ):
        # chunk = resample(chunk, ex.slowdown, 'linear')
        chunk = np.repeat(chunk, ex.slowdown, axis=0)
        chunks.append(chunk)
        buffered.put(chunk)
        if i >= buffer_first:
            audio.emit_queue.put(buffered.get(), False)
    while not buffered.empty():
        audio.emit_queue.put(buffered.get(), False)
    resampled = np.concatenate(chunks)
    time.sleep(ex.slowdown * record_time)
    save_file(ULTRAMICS, resampled, str(ex.pulse) + "__resampled")
    save_file(ULTRAMICS, rendered, str(ex.pulse) + "__pulse")
    save_file(ULTRAMICS, sample, str(ex.pulse))
    audio.record_stream.resume()
