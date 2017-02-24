import numpy as np

from stream import create_stream, SampleBuffer

class Recorder(object):
	def __init__(self, settings):
		self.buffer = SampleBuffer(channels=settings.input.channels)
                self.settings = settings
		self.stream = create_stream(
			settings=settings,
			output=False,
			callback=lambda *args: self._recording(*args)
		)

	def _recording(self, input, *rest):
		self.buffer.put(input)

	def sample(self):
		while not self.buffer.has():
			pass
		return self.buffer.get_chunk()

	def start(self):
		self.stream.start()

	def stop(self):
		self.stream.stop()

	def rate(self):
		return int(self.stream.samplerate)


