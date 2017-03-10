from __future__ import division

import time
import threading

import alsaaudio as aa
import numpy as np

import test

from audio import *
from config import *
from data import *
from device import *
from process import *
from pulse import *
from record import *
from save import *
from stream import *

from util import handle_close

handle_close()

dac = AudioDevice('dac', 192000)
ultramics = AudioDevice('ultramics', 192000)

input = Recorder(ultramics)
output = Stream(dac, False, True)

click = Click(dac, 5e3)

def take_sample():
	with emitters:
		t1 = time.time()
		# output.write_array(click.render())
	time.sleep(0.2)
	rec = input.get_recording(t1, 0.1)
	print rec
	save_file(ultramics, rec)

while True:
	take_sample()

