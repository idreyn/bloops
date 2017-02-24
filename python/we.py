from __future__ import division

import time

import alsaaudio as aa
import numpy as np

from config import *
from stream import *
from data import *

print aa.pcms()

input = Stream(Device('ultramics', 192000), True)
output = Stream(Device('dac', 192000), False)

t0 = time.time()

collected = []

while True:
	data = input.read_array(0.01)
        # data[:,1] = 0 * data[:,1]
        output.write_array(data)

print len(collected), len(collected[0])
	

