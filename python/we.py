from __future__ import division

import alsaaudio as aa
import numpy as np
from scikits.audiolab import play

from config import *
from stream import *
from data import *

print aa.pcms()

input = Stream(Device('ultramics', 192000), True)
output = Stream(Device('dac', 192000), False)
while True:
	data = input.read_array(2)
	output.write_array(data)
	

