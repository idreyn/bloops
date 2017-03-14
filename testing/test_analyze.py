import test, time
from scikits.audiolab import *
from process.analyze import *

sample = wavread("../../samples/weak-chirp.wav")[0]
t0 = time.time()
a = align(sample)
t1 = time.time()
print a, t1 - t0