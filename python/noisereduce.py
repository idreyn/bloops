import time
import wave

import numpy as np
from numpy.fft import *
from scipy.signal import *

import matplotlib.pyplot as plt

from config import *
from process import *

def hann_window(size):
	c0, c1, c2 = 0.5, -0.5, 0
	res = np.empty(size)
	for i in xrange(size):
		res[i] = c0 + c1 * cos(2.0 * np.pi * i / size) + c2 * cos(4.0 * np.pi * i / size)
	return res

def windowed(sample,window_size,overlap,hanning=True):
	assert 0 <= overlap < 1
	win = np.hanning(window_size)
	for start in xrange(0,len(sample),int(window_size * (1 - overlap))):
		sub = sample[start : start + window_size]
		if len(sub) < window_size: 
			sub = pad_to_size(sub,window_size)
		yield sub * win if hanning else sub

def count_windows(sample_length,window_size,overlap):
	return len(xrange(0,sample_length,int(window_size * (1 - overlap))))

class NoiseReduceSettings(object):
	def __init__(
		self,
		noise_gain=-30.0,
		sensitivity=10.0,
		window_size=1024,
		window_step=128,
		spectrum_median_window=1,
		freq_smoothing_bins=0,
		attack_time=0.02,
		attack_lookback_steps=1,
		release_time=0.1,
		double_window=False
	):
		self.noise_gain = noise_gain
		self.sensitivity = sensitivity
		self.window_size = window_size
		self.window_step = window_step
		self.spectrum_median_window = spectrum_median_window
		self.freq_smoothing_bins = freq_smoothing_bins
		self.attack_time = attack_time
		self.attack_lookback_steps = attack_lookback_steps
		self.release_time = release_time
		self.double_window = double_window


def noise_reduce(sample,noise,settings):
	t0 = time.time()
	# Check minimum noise length
	assert len(noise) > settings.window_size
	# Input constants
	NOISE_GAIN = settings.noise_gain # Gain (negative) for noise
	SENSITIVITY = settings.sensitivity # How much louder must a band be than avg. noise to pass?
	WINDOW_SIZE = settings.window_size # Window size (2 ** n)
	WINDOW_STEP = settings.window_step # Steps taken between each window (2 ** m)
	SPECTRUM_MEDIAN_WINDOW = settings.spectrum_median_window # Size of median window for spectrum grabbing
	FREQ_SMOOTHING_BINS = settings.freq_smoothing_bins # How many neighbors to use in frequency smoothing, if any
	ATTACK_TIME = settings.attack_time # Attack time
	RELEASE_TIME = settings.release_time # Release time
	ATTACK_LOOKBACK_STEPS = settings.attack_lookback_steps # How many windows to look back in attack step
	DOUBLE_WINDOW = settings.double_window # Whether to window twice during anaylsis and synthesis
	# Derived constants
	ATTACK_LOOKBACK = xrange(-1, - ATTACK_LOOKBACK_STEPS - 1, -1) # Range for use in attack
	OVERLAP = float(WINDOW_SIZE - WINDOW_STEP) / WINDOW_SIZE # What fraction of window (i) overlaps with window (i+1)?
	WINDOW_COUNT = count_windows(len(sample),WINDOW_SIZE,OVERLAP) # How many windows are there in total?
	N_ATTACK_BLOCKS = 1 + ATTACK_TIME * RATE / WINDOW_STEP # Attack blocks
	N_RELEASE_BLOCKS = 1 + RELEASE_TIME * RATE / WINDOW_STEP # Release blocks
	ATTACK_CONST = from_db(NOISE_GAIN / N_ATTACK_BLOCKS) # Attack decay constant
	RELEASE_CONST = from_db(NOISE_GAIN / N_RELEASE_BLOCKS) # Release decay constant
	NOISE_ATTEN_FACTOR = from_db(NOISE_GAIN) # Minimum attenuation factor
	SPECTRUM = xrange(WINDOW_SIZE) # Range of spectrum
	FINAL_ATTEN_FACTOR = 1 # How much to attenuate the final signal based on overlap
	# Prepare data arrays
	noise_f_db = noise_mean(noise,WINDOW_SIZE,OVERLAP,DOUBLE_WINDOW)
	window = hann_window(WINDOW_SIZE)
	gains = np.full((WINDOW_COUNT,WINDOW_SIZE),NOISE_ATTEN_FACTOR)
	spectra = np.empty((WINDOW_COUNT,WINDOW_SIZE),dtype=np.complex_)
	# Break the sample into frames using a Hanning window
	for i, frame in enumerate(windowed(sample,WINDOW_SIZE,OVERLAP,DOUBLE_WINDOW)):
		spectra[i] = fft(frame * window)
	# Calculate the gains for each sample based on noise reference
	for center in xrange(WINDOW_COUNT):
		if SPECTRUM_MEDIAN_WINDOW > 1:
			i0 = max(center - (SPECTRUM_MEDIAN_WINDOW / 2),0)
			i1 = min(center + (SPECTRUM_MEDIAN_WINDOW / 2) + 1,WINDOW_COUNT - 1)
			spectrum_med_db = to_db(np.median(spectra[i0:i1],0))
		else:
			spectrum_med_db = to_db(spectra[center])
		classify_gains(
			gains[center],
			spectrum_med_db,
			noise_f_db,
			SENSITIVITY * np.log(10),
			NOISE_ATTEN_FACTOR
		)
		# Now apply attack...
		attack(
			gains,
			center,
			SPECTRUM,
			ATTACK_LOOKBACK,
			ATTACK_CONST,
			NOISE_ATTEN_FACTOR
		)
		# ...and release
		release(
			gains,
			center,
			SPECTRUM,
			RELEASE_CONST,
			NOISE_ATTEN_FACTOR
		)
	'''
	attack(
		gains,
		len(gains) - 1,
		SPECTRUM,
		xrange(-1,-len(gains) -1,-1),
		ATTACK_CONST,
		NOISE_ATTEN_FACTOR
	)
	for center in xrange(len(gains)):
		release(
			gains,
			center,
			SPECTRUM,
			RELEASE_CONST,
			NOISE_ATTEN_FACTOR
		)
	'''
	# Apply smoothing if needed
	if FREQ_SMOOTHING_BINS:
		for i in xrange(WINDOW_COUNT):
			smooth(gains[i],FREQ_SMOOTHING_BINS,False)
	# Apply the gains!
	spectra = gains * spectra
	# Now rebuild the time domain signal
	result = np.empty(len(sample) + WINDOW_SIZE)
	for i, offset in enumerate(xrange(0,len(sample),WINDOW_STEP)):
		result[offset:offset+WINDOW_SIZE] = result[offset:offset+WINDOW_SIZE] + window * np.real(ifft(spectra[i]))
	# Good lord this took forever
	print time.time() - t0
	plt.plot(sample)
	plt.plot(result)
	plt.show()
	return result

def classify_gains(gains,sample_db,noise_db,sensitivity,gain_factor):
	for i in xrange(len(gains)):
		gains[i] = 1 if sample_db[i] > noise_db[i] + sensitivity else gain_factor

def noise_mean(noise,window_size,overlap,double=False):
	frames = 1 + len(noise) / (window_size * (1 - overlap))
	means = np.empty((frames,window_size))
	window = hann_window(window_size)
	for i, frame in enumerate(windowed(noise,window_size,overlap,double)):
		spectrum = fft(pad_to_size(frame,window_size) * window)
		means[i] = to_db(spectrum)
	return np.mean(means,0)

def attack(gains,center,spectrum,lookback,attack_const,min_gain):
	for freq in spectrum:
		for l in lookback:
			i = center + l
			if i < 0:
				break
			minimum = max(
				gains[i + 1][freq] * attack_const,
				min_gain
			)
			if minimum > gains[i][freq]:
				gains[i][freq] = minimum
			else:
				break

def release(gains,center,spectrum,release_const,min_gain):
	for freq in spectrum:
		if center > 0:
			gains[center][freq] = max(
				gains[center][freq],
				gains[center - 1][freq] * release_const,
				min_gain
			)

def smooth(sample,width=3,geom=True):
	ref = np.copy(sample)
	if geom:
		ref = to_db(ref)
	for i in xrange(len(sample)):
		i0 = max(0,i - width / 2)
		i1 = min(len(sample) - 1,1 + i + width / 2)
		avg = sum(ref[i0:i1]) / (i1 - i0)
		sample[i] = from_db(avg) if geom else avg
