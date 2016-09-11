import time
import numpy as np

import signal
import sys

from config import *
from data import *
from emit import *
from pulse import *

def signal_handler(signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

audio = PA()
output_device_index, output_device = choose_output(audio)
settings = Settings(device=output_device, np_format=np.float32)

emit = Emitter(audio, settings)
tone1 = Chirp(settings, 10000, 1000, 1e5)
silence = Silence(settings, 2.5e5)

while True:
	emit.enqueue(tone1.render())
	emit.enqueue(tone1.render())
	emit.enqueue(silence.render())
	time.sleep(0.5)
