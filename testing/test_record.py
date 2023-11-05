import time
import threading

import alsaaudio as aa
import numpy as np

import test

from audio import *
from config import *
from data import *
from device import *
from process import *
from pulse import *
from save import *
from stream import *

from util import handle_close

handle_close()

dac = AudioDevice("dac", 192000)
ultramics = AudioDevice("ultramics", 192000)

audio = Audio(ultramics, dac)
pulse = Chirp(ultramics, 6e4, 3e4, 5e3)


def take_sample():
    with audio as (record, emit, playback):
        with emitters:
            emit.write_array(pulse.render())
            rec = record.read_array(1)
    print(rec.shape)
    save_file(ultramics, rec)


try:
    while True:
        take_sample()
        time.sleep(0.05)
except KeyboardInterrupt:
    emitters.off()
