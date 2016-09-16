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
tone = Chirp(settings, 10000, 1000, 1e4)
tone2 = Chirp(settings, 1000, 10000, 1e4)
silence = Silence(settings, 2.5e5)

while True:
	emit.enqueue(tone.render())
	emit.enqueue(tone.render())
	time.sleep(0.75)
	emit.enqueue(tone2.render())
	emit.enqueue(tone2.render())
	time.sleep(3)
