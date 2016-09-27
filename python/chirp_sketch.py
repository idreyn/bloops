import time
import numpy as np

import signal
import sys

from config import *
from data import *
from emit import *
from record import *
from pulse import *

def signal_handler(signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

output_device = choose_output()
settings = Settings(device=output_device, np_format=np.float32)

e = Emitter(settings, output_device)

tone = Chirp(settings, 10000, 1000, 1e4)
tone2 = Chirp(settings, 1000, 10000, 1e4)

while True:
	e.start()
	e.emit(tone.render())
	e.emit(tone2.render())
	time.sleep(1)
