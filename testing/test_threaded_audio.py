import test
import time

from pulse import *
from config import *
from audio import *

a = Audio(ULTRAMICS, DAC)
a.start()

pulse = Chirp(1e2, 3e2, 1e6)

a.background_buffer.set_empty(0.1 * pulse.render(DAC))

delay = 0.1

try:
	while True:
		t0 = time.time()
		time.sleep(delay)
		samples = a.record_buffer.get(int(delay * ULTRAMICS.rate), t0)
		a.emit_buffer.put(samples)
except KeyboardInterrupt:
	pass

