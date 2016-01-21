import pyaudio
import serial
import time
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import *

from record import Recorder
from config import *
from process import *

def play_pulse(pulse,record_time=None):
	if not record_time:
		record_time = 200
	frames = []
	serial.write([pulse.start,pulse.end,pulse.ms_duration])
	for i, frame in enumerate(rec.record(float(record_time) / 1000)):
		frames.append(frame)
	data = frames_to_array(frames)
	t0 = time.time()
	data = bandpass(data,900 * pulse.low(),1100 * pulse.high()) * 3
	# data = noise_reduce(data,trim(data,0.5,1)) * 3
	print time.time() - t0
	new_frames = array_to_frames(data)
	stream = audio.open(
		format=FORMAT,
		channels=CHANNELS,
		rate=RATE/25,
		frames_per_buffer=CHUNK,
		output=True
	)
	for f in trim(new_frames,0,0.5):
		stream.write(f)
	stream.stop_stream()
	stream.close()


serial = serial.Serial(port=SERIAL_PORT,baudrate=SERIAL_BAUD,write_timeout=0.0)
audio = pyaudio.PyAudio()
rec = Recorder(audio)
chirp = Pulse(30,70,10)
bloop = Pulse(30,30,1)

while True:
	play_pulse(chirp)

