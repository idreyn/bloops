import time
import wave
from cmath import *

import numpy as np
from numpy.fft import *
from scipy.signal import *

import matplotlib.pyplot as plt
from scikits.audiolab import wavread, play

import pyaudio

from config import *
from process import *

class Record(object):
	def __init__(self,sample,spectrum,initial_gain):
		self.sample = sample
		self.spectrum = spectrum
		self.real = np.real(self.spectrum)
		self.imag = np.imag(self.spectrum)
		self.gains = np.repeat(initial_gain,len(spectrum))

	def invert(self):
		return np.real(ifft(self.spectrum * self.gains))

def pad_to_size(sample,length):
	zeroes = np.repeat(0,length - len(sample))
	return np.concatenate((sample,zeroes))

def open_wave(file):
	wf = wave.open(file,'rb')
	data = wf.readframes(CHUNK)
	while data != '':
		yield data
		data = wf.readframes(CHUNK)

def play_frames(audio,frames):
	stream = audio.open(
		format=FORMAT,
		channels=CHANNELS,
		rate=RATE/25,
		frames_per_buffer=CHUNK,
		output=True
	)
	for f in frames:
		stream.write(f)
	stream.close()

def hann_window(size):
	c0, c1, c2 = 0.5, -0.5, 0
	res = np.empty(size)
	for i in xrange(size):
		res[i] = c1 * cos(2.0 * np.pi * i / size) + c2 * cos(4.0 * np.pi * i / size)
	return res

def windowed(sample,window_size,overlap,hanning=True):
	assert 0 <= overlap < 1
	win = np.hanning(window_size)
	for start in xrange(0,len(sample),int(window_size * (1 - overlap))):
		sub = sample[start : start + window_size]
		yield sub * win[0:len(sub)] if hanning else sub

def to_db(val):
	return 10 * np.log10((0.00000001 + np.abs(val)) ** 2)

def from_db(val):
	return np.power(10,(1.0 / 20) * val)

def noise_reduce(sample,noise):
	t0 = time.time()
	NOISE_GAIN = -18.0
	SENSITIVITY = 4.0
	WINDOW_SIZE = 2048
	WINDOW_STEP = 128
	OVERLAP = float(WINDOW_SIZE - WINDOW_STEP) / WINDOW_SIZE
	CF = 0.375 * (1 - OVERLAP)
	ATTACK_TIME = 0.02
	RELEASE_TIME = 0.1
	N_ATTACK_BLOCKS = 1 + ATTACK_TIME * RATE / WINDOW_STEP
	N_RELEASE_BLOCKS = 1 + RELEASE_TIME * RATE / WINDOW_STEP
	ATTACK_CONST = from_db(NOISE_GAIN / N_ATTACK_BLOCKS)
	RELEASE_CONST = from_db(NOISE_GAIN / N_RELEASE_BLOCKS)
	ATTACK_LOOKBACK = 5
	NOISE_ATTEN_FACTOR = from_db(NOISE_GAIN)
	SPECTRUM = xrange(WINDOW_SIZE)
	noise_f_db = noise_mean(noise,WINDOW_SIZE,OVERLAP)
	records = []
	window = hann_window(WINDOW_SIZE)
	assert len(noise) > WINDOW_SIZE
	# Break the sample into frames using a Hanning window
	for frame in windowed(sample,WINDOW_SIZE,OVERLAP):
		if len(frame) < WINDOW_SIZE:
			frame = pad_to_size(frame,WINDOW_SIZE)
		f_sample = fft(frame * window)
		records.append(Record(frame,f_sample,NOISE_ATTEN_FACTOR))
	# Calculate the gains for each sample based on noise reference
	for i, rec in enumerate(records):
		i0 = max(i-2,0)
		i1 = min(i+3,len(records)-1)
		spectrum_med_db = to_db(np.median([r.spectrum for r in records[i0:i1]],0))
		rec.gains = gains(spectrum_med_db,noise_f_db,SENSITIVITY * np.log(10),NOISE_GAIN)
		# Now apply attack...
		for freq in SPECTRUM:
			lookback = xrange(i-1,i-ATTACK_LOOKBACK-1,-1)
			for i_lookback in lookback:
				if i_lookback < 0:
					break
				minimum = max(
					records[i_lookback + 1].gains[freq] * ATTACK_CONST,
					NOISE_ATTEN_FACTOR
				)
				if minimum > records[i_lookback]:
					records[i_lookback].gains[freq] = minimum
				else:
					break
		# ...and release
		for freq in SPECTRUM:
			if i > 0:
				records[i].gains[freq] = max(
					records[i].gains[freq],
					records[i-1].gains[freq] * RELEASE_CONST,
					NOISE_ATTEN_FACTOR
				)
	for rec in records:
		rec.gains = from_db(smooth(to_db(rec.gains),2))
	result = np.zeros(len(sample) + WINDOW_SIZE)
	for i, offset in enumerate(xrange(0,len(sample),WINDOW_STEP)):
		result[offset:offset+WINDOW_SIZE] = result[offset:offset+WINDOW_SIZE] + window * records[i].invert()
		# plt.plot(records[i].spectrum)
	print time.time() - t0
	print len(sample), len(result)
	plot_spectrum(fft(sample))
	plot_spectrum(fft(result))
	plt.show()
	return result

def attack(records,attack_coeff,min_gain):
	window_size = len(records[0].gains)
	for freq in xrange(window_size):
		for i in xrange(len(records)):
			if i > 0:
				mv = max(
					records[i].gains[freq],
					records[i-1].gains[freq] * attack_coeff,
					min_gain
				)
				records[i].gains[freq] = mv

def release(records,release_coeff,min_gain):
	window_size = len(records[0].gains)
	for freq in xrange(window_size):
		for i in reversed(xrange(len(records))):
			if i < len(records) - 1:
				mv = max(
					records[i].gains[freq],
					records[i+1].gains[freq] * release_coeff,
					min_gain
				)
				records[i].gains[freq] = mv

def noise_mean(noise,window_size,overlap):
	frames = 1 + len(noise) / (window_size * (1 - overlap))
	means = np.empty((frames,window_size))
	hanning = np.hanning(window_size)
	for i, frame in enumerate(windowed(noise,window_size,overlap)):
		spectrum = fft(pad_to_size(frame,window_size) * hanning)
		means[i] = to_db(spectrum)
	return np.mean(means,0)

def gains(sample_db,noise_db,sensitivity=10,gain=-100):
	res = np.empty(len(sample_db))
	gain_factor = from_db(gain)
	for i, (s,n) in enumerate(zip(sample_db,noise_db)):
		res[i] = 1 if s > n + sensitivity else gain_factor
	return res

def smooth(sample,width=3):
	res = np.empty(len(sample))
	for i in xrange(len(sample)):
		i0 = max(0,i - width / 2)
		i1 = min(len(sample) - 1,1 + i + width / 2)
		res[i] = sum(sample[i0:i1]) / (i1 - i0)
	return res

audio = pyaudio.PyAudio()
sample, sample_freq, encoding = wavread('sounds/single-bloop.wav')
sample = bandpass(sample,30000,50000)
noise = trim(sample,0,0.3)
sample = noise_reduce(sample,noise)
sample = bandpass(sample,30000,50000)
sample = 10 * sample
if True:
	data = pad_to_size(sample,CHUNK * (1 + len(sample) / CHUNK))
	data = array_to_frames(data)
	play_frames(audio,data)