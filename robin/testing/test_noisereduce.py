import time, sys
import pstats, cProfile
import sounddevice as sd
from scikits.audiolab import *

import test

from robin.plotting import *
from robin.process import *
from robin.noisereduce import noise_reduce, NoiseReduceSettings

def save(filename, data, rate):
    f = Sndfile(filename, 'w', Format('wav'), 1, rate)
    f.write_frames(data)
    f.close()

sample, rate, _ = wavread('../samples/single-bloop-trimmed.wav')
noise = wavread('../samples/single-bloop-noise.wav')[0]

cProfile.runctx(
	"reduced = noise_reduce(sample, noise, NoiseReduceSettings())",
	globals(), locals(), "profile.prof")

save('../samples/single-bloop-trimmed-reduced.wav', reduced, rate)

s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
