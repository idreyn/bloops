# encoding: utf-8
# cython: profile=False
# filename: noisereduce.pyx

import numpy as np
cimport numpy as np

from cpython cimport bool

from numpy.fft import *
from scipy.signal import *

from config import *
from process import *

cdef inline int int_max(int a, int b): return a if a >= b else b
cdef inline int int_min(int a, int b): return a if a <= b else b
cdef inline double double_max(double a, double b): return a if a >= b else b
cdef inline double double_min(double a, double b): return a if a <= b else b

def hann_window(int size):
	cdef double c0 = 0.5
	cdef double c1 = -0.5
	cdef double c2 = 0.0
	cdef np.ndarray[double, ndim=1] res = np.empty(size)
	cdef int i
	for i in xrange(size):
		res[i] = c0 + c1 * cos(2.0 * np.pi * i / size) + c2 * cos(4.0 * np.pi * i / size)
	return res

def windowed(np.ndarray[double, ndim=1] sample,int window_size,double overlap,bool hanning=True):
	assert 0 <= overlap < 1
	cdef int num_windows = count_windows(len(sample),window_size,overlap)
	cdef np.ndarray[double, ndim=2] res = np.empty((num_windows,window_size))
	cdef np.ndarray[double, ndim=1] win = np.hanning(window_size)
	cdef int i, start
	cdef np.ndarray[double, ndim=1] sub
	for i, start in enumerate(xrange(0,len(sample),int(window_size * (1 - overlap)))):
		sub = sample[start : start + window_size]
		if len(sub) < window_size: 
			sub = pad_to_size(sub,window_size)
		res[i] = sub
	return res

def count_windows(int sample_length,int window_size,double overlap):
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
		attack_lookback_steps=5,
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
	# Check minimum noise length
	assert len(noise) > settings.window_size
	# Input constants
	cdef double NOISE_GAIN = settings.noise_gain # Gain (negative) for noise
	cdef double SENSITIVITY = settings.sensitivity # How much louder must a band be than avg. noise to pass?
	cdef int WINDOW_SIZE = settings.window_size # Window size (2 ** n)
	cdef int WINDOW_STEP = settings.window_step # Steps taken between each window (2 ** m)
	cdef int SPECTRUM_MEDIAN_WINDOW = settings.spectrum_median_window # Size of median window for spectrum grabbing
	cdef int FREQ_SMOOTHING_BINS = settings.freq_smoothing_bins # How many neighbors to use in frequency smoothing, if any
	cdef double ATTACK_TIME = settings.attack_time # Attack time
	cdef double RELEASE_TIME = settings.release_time # Release time
	cdef int ATTACK_LOOKBACK_STEPS = settings.attack_lookback_steps # How many windows to look back in attack step
	cdef bool DOUBLE_WINDOW = settings.double_window # Whether to window twice during anaylsis and synthesis
	# Derived constants
	cdef double OVERLAP = float(WINDOW_SIZE - WINDOW_STEP) / WINDOW_SIZE # What fraction of window (i) overlaps with window (i+1)?
	cdef int WINDOW_COUNT = count_windows(len(sample),WINDOW_SIZE,OVERLAP) # How many windows are there in total?
	cdef int N_ATTACK_BLOCKS = 1 + ATTACK_TIME * RATE / WINDOW_STEP # Attack blocks
	cdef int N_RELEASE_BLOCKS = 1 + RELEASE_TIME * RATE / WINDOW_STEP # Release blocks
	cdef double ATTACK_CONST = from_db(NOISE_GAIN / N_ATTACK_BLOCKS) # Attack decay constant
	cdef double RELEASE_CONST = from_db(NOISE_GAIN / N_RELEASE_BLOCKS) # Release decay constant
	cdef double NOISE_ATTEN_FACTOR = from_db(NOISE_GAIN) # Minimum attenuation factor
	SPECTRUM = xrange(WINDOW_SIZE) # Range of spectrum
	FINAL_ATTEN_FACTOR = 1 # How much to attenuate the final signal based on overlap
	# Prepare data arrays
	cdef np.ndarray[double, ndim=1] noise_f_db = noise_mean(noise,WINDOW_SIZE,OVERLAP,DOUBLE_WINDOW)
	cdef np.ndarray[double, ndim=1] window = hann_window(WINDOW_SIZE)
	cdef np.ndarray[double, ndim=2] gains = np.full((WINDOW_COUNT,WINDOW_SIZE),NOISE_ATTEN_FACTOR)
	cdef np.ndarray[np.complex_t, ndim=2] spectra = np.empty((WINDOW_COUNT,WINDOW_SIZE),dtype=np.complex_)
	cdef int i, i0, i1, center, offset
	cdef np.ndarray[double, ndim=1] frame, spectrum_med_db
	# Break the sample into frames using a Hanning window
	for i, frame in enumerate(windowed(sample,WINDOW_SIZE,OVERLAP,DOUBLE_WINDOW)):
		spectra[i] = fft(frame * window)
	# Calculate the gains for each sample based on noise reference
	for center in xrange(WINDOW_COUNT):
		if SPECTRUM_MEDIAN_WINDOW > 1:
			i0 = int_max(center - (SPECTRUM_MEDIAN_WINDOW / 2),0)
			i1 = int_max(center + (SPECTRUM_MEDIAN_WINDOW / 2) + 1,WINDOW_COUNT - 1)
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
			ATTACK_LOOKBACK_STEPS,
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
	# Apply smoothing if needed
	if FREQ_SMOOTHING_BINS:
		for i in xrange(WINDOW_COUNT):
			smooth(gains[i],FREQ_SMOOTHING_BINS,False)
	# Apply the gains!
	spectra = gains * spectra
	# Now rebuild the time domain signal
	cdef np.ndarray[double, ndim=1] result = np.empty(len(sample) + WINDOW_SIZE)
	i = 0
	for offset in xrange(0,len(sample),WINDOW_STEP):
		result[offset:offset+WINDOW_SIZE] = result[offset:offset+WINDOW_SIZE] + window * np.real(ifft(spectra[i]))
		i = i + 1
	# Good lord this took forever
	return result

def classify_gains(np.ndarray[double, ndim=1] gains,np.ndarray[double, ndim=1] sample_db,np.ndarray[double, ndim=1] noise_db,double sensitivity,double gain_factor):
	cdef int i
	for i in xrange(len(gains)):
		gains[i] = 1 if sample_db[i] > noise_db[i] + sensitivity else gain_factor

def noise_mean(np.ndarray[double, ndim=1] noise,int window_size,double overlap,bool double=False):
	cdef int frames = 1 + int(len(noise) / (window_size * (1 - overlap)))
	cdef int i
	cdef np.ndarray[double, ndim=2] means = np.empty((frames,window_size))
	cdef np.ndarray[double, ndim=1] window = hann_window(window_size)
	for i, frame in enumerate(windowed(noise,window_size,overlap,double)):
		spectrum = fft(pad_to_size(frame,window_size) * window)
		means[i] = to_db(spectrum)
	return np.mean(means,0)

def attack(np.ndarray[double, ndim=2] gains,int center,spectrum,int lookback_steps,double attack_const,double min_gain):
	cdef int freq
	cdef int l
	cdef int i
	cdef double minimum
	cdef lookback = xrange(-1, - lookback_steps - 1, -1)
	for freq in spectrum:
		for l in lookback:
			i = center + l
			if i < 0:
				break
			minimum = double_max(
				gains[i + 1,freq] * attack_const,
				min_gain
			)
			if minimum > gains[i,freq]:
				gains[i,freq] = minimum
			else:
				break

def attack_one(np.ndarray[double, ndim=2] gains,int center,spectrum,double attack_const,double min_gain):
	cdef int freq
	cdef double minimum
	for freq in spectrum:
		if center - 1 < 0:
			break
		minimum = double_max(
			gains[center,freq] * attack_const,
			min_gain
		)
		if minimum > gains[center - 1,freq]:
			gains[center - 1,freq] = minimum
		else:
			break

def release(np.ndarray[double, ndim=2] gains,int center,spectrum,double release_const,double min_gain):
	cdef int freq
	for freq in spectrum:
		if center > 0:
			gains[center,freq] = double_max(
				gains[center,freq],
				double_max(
					gains[center - 1,freq] * release_const,
					min_gain
				)
			)

def smooth(np.ndarray[double, ndim=1] sample,int width=3,bool geom=True):
	cdef np.ndarray[double, ndim=1] ref = np.copy(sample)
	cdef int i, i0, i1
	cdef double avg
	if geom:
		ref = to_db(ref)
	for i in xrange(len(sample)):
		i0 = int_max(0,i - width / 2)
		i1 = int_min(len(sample) - 1,1 + i + width / 2)
		avg = sum(ref[i0:i1]) / (i1 - i0)
		sample[i] = from_db(avg) if geom else avg