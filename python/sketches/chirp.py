import time
import sketch

from config import *
from emit import *
from pulse import *
from util import handle_close

handle_close()

output = choose_output()
print output.name

settings = Settings(output_device=output)
e = Emitter(settings)

tone = Chirp(settings.output, 10000, 1000, 1e5)
tone2 = Chirp(settings.output, 1000, 10000, 1e4)

e.start()
e.emit(tone.render())
e.emit(tone2.render())
time.sleep(1)
