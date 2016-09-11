from multiprocessing import Queue
import pyaudio
import numpy as np

from pulse import Silence
from data import AudioData

def playback(stream, queue):
	while True:
		stream.write(queue.get())

class Emitter(object):
	def __init__(self, audio, settings, device_index=None):
		self.audio = audio
		self.settings = settings
		self.queue = Queue()
		def do_stream(*args):
			return self.do_stream(*args)
		self.stream = audio.open(
			format=settings.pa_format,
			channels=settings.channels,
			rate=settings.rate,
			output=True,
			stream_callback=do_stream
		)

	def enqueue(self, arr):
		frame_size = self.settings.frame_size
		frames = AudioData.from_array(self.settings, arr).frames
		for f in frames:
			f = f + "\x00" * (frame_size - len(f))
			self.queue.put(f)

	def do_stream(self, *args):
		return (self.queue.get(), pyaudio.paContinue)