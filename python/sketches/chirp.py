import time
import sketch

from config import *
from emit import *
from pulse import *
from util import handle_close

handle_close()

output = choose_output()

settings = Settings(output_device=output)
e = Emitter(settings)

tone = Chirp(settings, 10000, 1000, 1e5)
tone2 = Chirp(settings, 1000, 10000, 1e5)

while True:
	e.start()
	e.emit(tone.render())
	e.emit(tone2.render())
	time.sleep(1)
