import time
import sketch

from config import *
from emit import *
from pulse import *
from record import *

from process import bandpass
from util import handle_close, resample

import numpy as np

handle_close()

output = choose_output()
input = choose_input()

output.rate = 192000

print output.name
print input.name

settings = Settings(
	output_device=output,
	input_device=input
)

e = Emitter(settings)
r = Recorder(settings)

LOW = 30000
HIGH = 50000

tone = Chirp(settings, HIGH, LOW, 1e4)
tone2 = Chirp(settings, LOW, HIGH, 1e4)

click1 = Click(settings, 1e3)
click2 = Tone(settings, LOW, 5e2)

def chirp_once():
	print "chirp!"
	e.start()
	r.start()
	time.sleep(0.05)
	e.emit(tone.render())
	time.sleep(0.12)
	r.stop()
	sample = 3 * bandpass(
		r.buffer.get_samples(),
		20000,
		80000,
		settings.input.rate
	)
	sample = np.repeat(sample, 10, axis=0)
	e.emit(sample)
	time.sleep(2)

if __name__ == "__main__":
	while True:
		chirp_once()
