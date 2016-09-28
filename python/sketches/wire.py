import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from util import handle_close

from config import *
from emit import *
from record import *

handle_close()

output_device = choose_output()
input_device = choose_input()

settings = Settings(device=input_device)

e = Emitter(settings, output_device)
r = Recorder(settings, input_device)

r.start()
e.start()

while True:
	e.emit(r.sample())
