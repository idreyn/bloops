import test, time
from scikits.audiolab import *

from util import bandpass
from process.analyze import *

sample, rate, fmt = wavread("../../samples/crazy-combined-chirp.wav")
left, right = map(
	lambda s: bandpass(s, 2e4, 9e4, rate),
	[sample[:,0], sample[:,1]]
)

"""
plt.plot(moving_average(left ** 2, 100))
plt.plot(moving_average(right ** 2, 100))
plt.show()
"""

t0 = time.time()
left, right = align_samples(left, right, silence_boundary_index=1100)
t1 = time.time()

"""
plt.plot(moving_average(left ** 2, 100))
plt.plot(moving_average(right ** 2, 100))
plt.show()
"""

print t1 - t0