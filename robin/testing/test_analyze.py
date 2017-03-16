import test, time
from scikits.audiolab import *
from process.analyze import *

sample = wavread("../../samples/stereo-chirp-no-registration.wav")[0]
t0 = time.time()
a = align(sample)
t1 = time.time()
print a, 1000 * (t1 - t0)