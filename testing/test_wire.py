import test
import time

from config import *
from stream import *

if not has_required_devices():
	print "missing hardware"
	print_device_availability()
else:
	input = Stream(ULTRAMICS, True)
	output = Stream(DAC, False, False)
	try:
		while True:
			output.write(input.read())
	except KeyboardInterrupt:
		pass
