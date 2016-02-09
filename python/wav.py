import struct
import numpy as np

from process import *
from config import *

def open_wave(file):
	wf = wave.open(file,'rb')
	data = wf.readframes(CHUNK)
	while data != '':
		yield data
		data = wf.readframes(CHUNK)

def play_array(audio,data,rate_mutliplier=1,channels=None):
	data = pad_to_size(data,CHUNK * (1 + len(data) / CHUNK))
	frames = array_to_frames(data)
	play_frames(audio,frames,rate_mutliplier,channels=channels)

def play_frames(audio,frames,rate_mutliplier=1,channels=None,):
	stream = audio.open(
		format=FORMAT,
		channels=channels or CHANNELS,
		rate=int(RATE * rate_mutliplier),
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