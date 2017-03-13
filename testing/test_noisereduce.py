import time, sys
import pstats, cProfile

import sounddevice as sd
from scikits.audiolab import *
sys.path.append('..')

from robin.plotting import *
from robin.process import *
from robin.noisereduce import noise_reduce, NoiseReduceSettings
import time
import pstats, cProfile

from scikits.audiolab import wavread

import test
from process import *
from noisereduce import noise_reduce, NoiseReduceSettings

audio = pyaudio.PyAudio()

def noise_reduce_test():
	sample = wavread('../../sounds/single-bloop-trimmed.wav')[0]
	noise = wavread('../../sounds/single-bloop-noise.wav')[0]
	sample = bandpass(sample,30000,50000)
	t0 = time.time()
	sample = noise_reduce(sample,noise,NoiseReduceSettings())
	print 'noise filter in time:', round(time.time() - t0,2)
	if True:	
		save('../samples/single-bloop-trimmed-reduced.wav', reduced, rate)
		plot_samples(sample, 0.5 * reduced)

def save(filename, data, rate):
    f = Sndfile(filename, 'w', Format('wav'), 1, rate)
    f.write_frames(data)
    f.close()

cProfile.runctx("res = noise_reduce_test()",globals(),locals(),"profile.prof")
s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
