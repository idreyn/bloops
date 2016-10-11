import sketch

from config import *
from emit import *
from record import *
from util import handle_close, resample

handle_close()

output_device = choose_output()
input_device = choose_input()

settings = Settings(
	input_device=choose_input(), 
	output_device=choose_output()
)

print settings.input.name, settings.input.rate, settings.input.channels
print settings.output.name, settings.output.rate, settings.output.channels

e = Emitter(settings)
r = Recorder(settings)

r.start()
e.start()

while True:
	e.emit(r.sample())
