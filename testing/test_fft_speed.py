
from __future__ import division

import test
import time

from scipy.fftpack import *
import matplotlib.pyplot as plt

from config import *
from pulse import *

dac = AudioDevice('dac', rate=192000, channels=2)
sample = Chirp(dac, 5e4, 2e4, 1e3).render()

total = 0
num = 100
for i in xrange(num):
	t0 = time.time()
	fft(sample)
	total += time.time() - t0
avg_time = total / num
print 1000 * avg_time