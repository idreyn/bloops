
from __future__ import division
import time
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

class Echolocation(object):

    def __init__(self, pulse, slowdown, device,
                 us_record_duration=1e5, us_silence_before=1e4):
        self.pulse = pulse
        self.slowdown = slowdown
        self.device = device
        self.us_silence_before = us_silence_before
        self.us_record_duration = us_record_duration


def simple_loop(ex, audio, profile, pipeline=None):
    assert isinstance(ex, Echolocation)
    rendered = ex.pulse.render(DAC)
    with emitter_enable:
        audio.emit_queue.put(rendered)
        t0 = time.time()
        audio.record_buffer.clear()
        record_time = 1e-6 * (ex.us_record_duration + ex.us_silence_before)
        time.sleep(record_time)
        sample = audio.record_buffer.get(
            int(record_time * audio.record_stream.device.rate), 
            t0 - ex.us_silence_before
        )
    audio.record_stream.pause()
    if pipeline:
        t0 = time.time()
        sample = pipeline.run(ex, sample)
        print "Pipeline ran in", round(time.time() - t0, 3)
    chunks = []
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
    if profile.should_play_recording():
        while not buffered.empty():
            audio.emit_queue.put(buffered.get(), False)
    resampled = np.concatenate(chunks)
    if profile.should_play_recording():
        time.sleep(ex.slowdown * record_time)
    else:
        print "Playback disabled in profile"
    prefix = profile.save_prefix() + "_" + str(ex.pulse)
    print "Saving..."
    if profile.should_save_recording():
        save_file(ULTRAMICS, sample, prefix)
    if profile.should_save_resampled():
        save_file(ULTRAMICS, resampled, prefix + "__resampled")
    if profile.should_save_pulse():
        save_file(ULTRAMICS, rendered, prefix + "__pulse")
    audio.record_stream.resume()
    print "Done"
