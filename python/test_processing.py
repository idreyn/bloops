import time

from scikits.audiolab import wavread
from process import *
from noisereduce import noise_reduce, NoiseReduceSettings

audio = pyaudio.PyAudio()
sample, sample_freq, encoding = wavread('../sounds/single-bloop.wav')
sample = bandpass(sample,30000,50000)
noise = trim(sample,0,0.1)
plt.plot(sample)
t0 = time.time()
sample = noise_reduce(sample,noise,NoiseReduceSettings())
print 'noise filter in time:', round(time.time() - t0,2)
plt.show()
sample = from_db(20) * sample
if True:
	data = pad_to_size(sample,CHUNK * (1 + len(sample) / CHUNK))
	data = array_to_frames(data)
	play_frames(audio,data,0.04)