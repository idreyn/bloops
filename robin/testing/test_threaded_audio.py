import test
import time

from pulse import *
from config import *
from audio import *

a = Audio(ULTRAMICS, DAC)
a.start()

pulse = Chirp(1e2, 1.2e2, 1e6)
print pulse

try:
	while True:
		delay = 0.01
		t0 = time.time()
		time.sleep(delay)
		samples = a.record_buffer.get_samples(int(delay * ULTRAMICS.rate), t0)
		a.emit_buffer.put_samples(samples)
except KeyboardInterrupt:
	pass

