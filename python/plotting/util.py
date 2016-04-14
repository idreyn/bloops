import numpy as np
import matplotlib.pyplot as plt

from config import *

def plot_spectrum(spectrum):
	time_step = 1.0 / RATE
	ps = np.abs(spectrum) ** 2
	freqs = np.fft.fftfreq(spectrum.size, time_step)
	idx = np.argsort(freqs)
	plt.plot(freqs[idx],ps[idx])

def plot_stereo(time,left,right):
	f, axes = plt.subplots(2,sharex=True)
	axes[0].plot(time,left)
	axes[0].set_title('Left')
	axes[1].plot(time,right)
	axes[1].set_title('Right')
	return axes

def plot_here(x,y):
	plt.plot(x,y)
	plt.show()