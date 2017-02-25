import time, sys
import pstats, cProfile

import sounddevice as sd
from scikits.audiolab import wavread

sys.path.append('..')


from robin.plotting import *
from robin.process import *
from robin.noisereduce import noise_reduce, NoiseReduceSettings

# audio = pyaudio.PyAudio()

def noise_reduce_test():
	sample, rate, enc = wavread('../samples/single-bloop-trimmed.wav')
	noise = wavread('../samples/single-bloop-noise.wav')[0]
	sample = bandpass(sample,30000,50000,rate)
	t0 = time.time()
	sample = noise_reduce(sample,noise,NoiseReduceSettings(window_size=64))
	print 'noise filter in time:', round(time.time() - t0,2)
	sample = from_db(20) * sample
	if True:
		sd.play(sample, rate)
		
cProfile.runctx("res = noise_reduce_test()",globals(),locals(),"profile.prof")
s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_title()
