from __future__ import division

import time
import threading

import alsaaudio as aa
import numpy as np

from config import *
from stream import *
from data import *
from record import *
from pulse import *

from util import handle_close

print aa.pcms()

handle_close()


dac = Device('dac', 192000)
output = Stream(dac, False, False)

# ultramics = Device('ultramics', 192000)
# input = Recorder(ultramics)

click = Click(dac, 1e3)

while True:
	time.sleep(1)
	output.write_array(click.render())
