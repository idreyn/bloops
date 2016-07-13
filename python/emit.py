from multiprocessing import Queue

import pyaudio

from data import AudioData

class Emitter(object):
	def __init__(self, audio, settings, device_index=None):
		self.audio = audio
		self.settings = settings
		def do_stream(a, b, c, d):
			return self.do_stream(a, b, c, d)
		self.stream = audio.open(
			format=settings.pa_format,
			channels=settings.channels,
			rate=settings.rate,
			output=True,
			stream_callback=do_stream,
			output_device_index=device_index
		)
		self.clear_queue()

	def clear_queue(self):
		self.queue = Queue()

	def play(self, arr):
		self.clear_queue()
		for f in AudioData.from_array(self.settings, arr).frames:
			self.queue.put(f)

	def do_stream(self, a, b, c, d):
		next = None
		if not self.queue.empty():
			next = self.queue.get(True)
		return (next, pyaudio.paContinue)

	def start(self):
		self.playing = True
		self.stream.start_stream()

	def stop(self):
		self.playing = False
		self.stream.stop_stream()