import pyaudio
import serial
import time
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import *

from record import Recorder
from config import *

class Pulse(object):
	def __init__(self,start,end,duration):
		self.start = start
		self.end = end
		self.duration = duration

def plot_spectrum(data):
	time_step = 1.0 / RATE
	ps = np.abs(np.fft.fft(data)) ** 2
	freqs = np.fft.fftfreq(data.size, time_step)
	idx = np.argsort(freqs)
	plt.plot(freqs[idx], ps[idx])

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
	print arr
	return arr * NORMALIZE

def array_to_frames(arr):
	NORMALIZE = 1.0
	frames = []
	arr = (arr * NORMALIZE)
	print arr
	res = np.ndarray.tolist(arr)
	for chunk in chunks(res,CHUNK):
		format = "%df" % CHUNK
		frames.append(struct.pack(format,*chunk))
	return frames

def design_filter(lowcut, highcut, fs, order=3):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b,a = butter(order, [low,high], btype='band')
	return b,a

def bandpass(data,low,high):
	bpf = design_filter(low,high,RATE)
	return lfilter(bpf[0],bpf[1],data)

def play_pulse(pulse,record_time=None):
	if not record_time:
		record_time = 100
	t0 = time.time()
	frames = []
	serial.write([pulse.start,pulse.end,pulse.duration])
	for i, frame in enumerate(rec.record(float(record_time) / 1000)):
		frames.append(frame)
	data = frames_to_array(frames)
	filtered = bandpass(data,30000,35000) * 10
	new_frames = array_to_frames(filtered)
	stream = audio.open(
		format=FORMAT,
		channels=CHANNELS,
		rate=RATE/25,
		frames_per_buffer=CHUNK,
		output=True
	)
	for f in new_frames:
		stream.write(f)
	stream.stop_stream()
	stream.close()


serial = serial.Serial(port=SERIAL_PORT,baudrate=SERIAL_BAUD,write_timeout=0.0)
audio = pyaudio.PyAudio()
rec = Recorder(audio)

chirp_up = Pulse(30,50,5)
bloop = Pulse(30,30,5)

while True:
	play_pulse(chirp_up)
