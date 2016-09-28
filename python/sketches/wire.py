import time
import sys

sys.path.append('..')

from util import handle_close

from config import *
from data import *
from emit import *
from record import *

handle_close()

output_device = choose_output()
input_device = choose_input()

settings = Settings(device=output_device)

e = Emitter(settings, output_device)
r = Recorder(settings, input_device)

r.start()
e.start()

while True:
	e.emit(r.sample())
