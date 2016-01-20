import struct
from cmath import *
from math import *

import numpy as np
from numpy.fft import *

import matplotlib.pyplot as plt
from scipy.signal import *

from config import *

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
		rate=RATE/50,
		frames_per_buffer=CHUNK,
		output=True
	)
	for f in frames:
		stream.write(f)
	stream.close()

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def frames_to_array(frames):
	NORMALIZE = 1.0
	res = []
	for frame in frames:
		format = "%df" % CHUNK
		res = res + list(struct.unpack(format,frame))
	arr = np.array(res) 
	return arr * NORMALIZE

def array_to_frames(arr):
	NORMALIZE = 1.0
	frames = []
	arr = (arr * NORMALIZE)
	res = np.ndarray.tolist(arr)
	for chunk in chunks(res,CHUNK):
		format = "%df" % CHUNK
		frames.append(struct.pack(format,*chunk))
	return frames

def bandpass_coefficients(lowcut, highcut, fs, order=3):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b,a = butter(order, [low,high], btype='band')
	return b,a

def bandpass(data,low,high):
	bpf = bandpass_coefficients(low,high,RATE)
	return lfilter(bpf[0],bpf[1],data)

def trim(arr,start,end=1):
	start_ind = int(round(start * len(arr)))
	end_ind = int(round(end * len(arr)))
	return arr[start_ind:end_ind]

def pad_to_size(sample,length):
	zeroes = np.repeat(0,length - len(sample))
	return np.concatenate((sample,zeroes))

def to_db(val):
	return 10 * np.log10((0.00000001 + np.abs(val)) ** 2)

def from_db(val):
	return np.power(10,(1.0 / 20) * val)