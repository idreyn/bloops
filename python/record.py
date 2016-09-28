from stream import create_stream, transposed, SampleBuffer

class Recorder(object):
	def __init__(self, settings, device):
		self.buffer = SampleBuffer()
		self.stream = create_stream(
			settings=settings,
			device=device,
			output=False,
			callback=lambda *args: self.record(*args)
		)

	def record(self, input, *rest):
		# Put transposed version because sounddevice expects transposed shape
		# relative to what the rest of the system uses, e.g. (len, channels)
		# instead of (channels, len).
		self.buffer.put(transposed(input))

	def sample(self):
		while not self.buffer.has():
			pass
		return self.buffer.get_chunk()

	def start(self):
		self.stream.start()

	def stop(self):
		self.stream.stop()


