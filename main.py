from __future__ import division

import time
import threading

import alsaaudio as aa
import numpy as np

from config import *
from data import *
from device import *
from process import *
from pulse import *
from record import *
from save import *

from util import handle_close

handle_close()

dac = AudioDevice('dac', 192000)
ultramics = AudioDevice('ultramics', 192000)

input = None
output = None

def ready_streams():
	global input, output
	try:
		if not input:
			input = Recorder(ultramics)
		if not output:
			output = Stream(dac, False, False)
		return True
	except:
		input = None
		output = None
		return False

def take_sample():
	if ready_streams():
		t0 = time.time()
		with emitters:
			t1 = time.time()
			output.write_array(click.render())
		time.sleep(0.2)
		rec = input.get_recording(t1, 0.1)
		# rec = EnvironmentSample(rec, ultramics.rate, 0).process()
		save_file(ultramics, rec)

take_sample()

