import sketch

from config import *
from emit import *
from record import *
from util import handle_close

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
