import time
from os import path
import numpy as np

from robin.audio import Audio
from robin.config import BATHAT, ULTRAMIC
from robin.gpio import emitter_enable
from robin.pulse import Tone
from robin.process.analyze import split_on_silence

audio = Audio(emit_device=BATHAT, record_device=ULTRAMIC)
audio.start(record_capacity_periods=2000)

def get_tone_ladder_recording(frequencies, tone_length):
    tones = [
        Tone(freq, tone_length).render(BATHAT)
        for freq in frequencies
    ]
    start_time = time.time() 
    with emitter_enable:
        for tone in tones:
            audio.add_to_emit(tone)
            time.sleep(0.1)
    end_time = time.time()
    recording = audio.record_buffer.get_for_interval(start_time, end_time)
    return recording
