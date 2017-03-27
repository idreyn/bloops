import test
import time

from pulse import *
from config import *
from audio import *

a = Audio(ULTRAMICS, DAC)
a.start()

pulse = Tone(3.4e2, 1e6)
print pulse

try:
	while True:
		a.emit_buffer.put(pulse.render(DAC))
		time.sleep(0)
except KeyboardInterrupt:
	pass