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
	'''
	sample = from_db(20) * sample
	if True:
		data = pad_to_size(sample,CHUNK * (1 + len(sample) / CHUNK))
		data = array_to_frames(data)
		play_frames(audio,data,0.04)
	'''


cProfile.runctx("res = noise_reduce_test()",globals(),locals(),"profile.prof")
s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
