import time
import sys

sys.path.append('..')

from util import handle_close

from config import *
from data import *
from emit import *
from pulse import *

handle_close()

output_device = choose_output()
settings = Settings(device=output_device)

e = Emitter(settings, output_device)

tone = Chirp(settings, 10000, 1000, 1e4)
tone2 = Chirp(settings, 1000, 10000, 1e4)

while True:
	e.start()
	e.emit(tone.render())
	e.emit(tone2.render())
	time.sleep(1)
