import pyaudio
import serial
import time
import struct
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import *

from record import Recorder
from config import *

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def frames_to_array(frames):
	NORMALIZE = 1.0 / 32768
	res = []
	for frame in frames:
		format = "%di" % CHUNK
		res = res + list(struct.unpack(format,frame))
	return np.array(res) * NORMALIZE

def array_to_frames(arr):
	NORMALIZE = 32768
	frames = []
	res = np.ndarray.tolist(arr * NORMALIZE)
	for chunk in chunks(res,CHUNK):
		format = "%di" % CHUNK
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

def pulse(kHz_start,kHz_end,duration,record_time):
	t0 = time.time()
	frames = []
	serial.write([kHz_start,kHz_end,duration])
	for i, frame in enumerate(rec.record(float(record_time) / 1000)):
		frames.append(frame)
		print md5.new(str(frame)).digest()
	data = frames_to_array(frames)
	filtered = (bandpass(data,30000,50000) * 2).clip(-32767,32768 )
	new_frames = array_to_frames(filtered)
	stream = audio.open(
		format=FORMAT,
		channels=CHANNELS,
		rate=RATE/15,
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

while True:
	pulse(30,30,5,100)
