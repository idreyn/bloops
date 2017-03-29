import test
import time

from pulse import *
from config import *
from audio import *

a = Audio(ULTRAMICS, DAC)
a.start()

pulse = Chirp(1e2, 3e2, 1e6)

delay = 0.01

try:
	while True:
		time.sleep(delay)
		# samples = a.record_buffer.get_samples(int(delay * ULTRAMICS.rate), t0)
		# a.emit_buffer.put_samples(samples)
except KeyboardInterrupt:
	pass

