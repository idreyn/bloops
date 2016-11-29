import alsaaudio as aa
from config import *
from stream import *

import time

print aa.pcms()

d = Device('ultramics', 192000)
s = Stream(d, True)
while True:
	t0 = time.time()
	print s.read_array(2).shape
	print time.time() - t0
