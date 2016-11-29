from __future__ import division

import alsaaudio as aa
import numpy as np
from scikits.audiolab import play

from config import *
from stream import *

print aa.pcms()

d = Device('ultramics', 192000)
s = Stream(d, True)
while True:
	data = (1 / 32768) * np.transpose(s.read_array(0.1))
	play(data, 20000)
