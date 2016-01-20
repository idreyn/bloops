import numpy as np
import matplotlib.pyplot as plt

def plot_spectrum(spectrum):
	time_step = 1.0 / RATE
	ps = np.abs(spectrum) ** 2
	freqs = np.fft.fftfreq(spectrum.size, time_step)
	idx = np.argsort(freqs)
	plt.plot(freqs[idx],ps[idx])