import numpy as np
from scikits.audiolab import *
from scipy.fftpack import *
import matplotlib.pyplot as plt

from process import *

def plot_spectrum(spectrum):
	time_step = 1.0 / RATE
	ps = np.abs(spectrum) ** 2
	freqs = np.fft.fftfreq(spectrum.size, time_step)
	idx = np.argsort(freqs)
	plt.plot(freqs[idx],ps[idx])

data, RATE, enc = wavread('../resources/recordings/single-downchirp.wav')
t = 1.0
n = t * RATE
d0 = data[:,0][0:n]
d0 = bandpass(d0,20000,60000)
sw = np.sin(35000 * 2 * np.pi * np.linspace(0,1,len(d0)))
res = sw * d0
noise = res[0:30000]
plt.plot(data)
plt.plot(res)
plt.show()
res = bandpass(data,1000,10000)
play(res)