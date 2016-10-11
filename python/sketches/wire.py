import sketch

from config import *
from emit import *
from record import *
from util import handle_close

handle_close()

output_device = choose_output()
input_device = choose_input()

settings = Settings(
	input_device=choose_input(), 
	output_device=choose_output()
)

print settings.input.name, settings.input.rate, settings.input.channels
print settings.output.name, settings.output.rate, settings.output.channels

if settings.must_resample():
	raise Exception("Resampling not implemented yet")

e = Emitter(settings, output_device)
r = Recorder(settings, input_device)

r.start()
e.start()

while True:
	e.emit(r.sample())
