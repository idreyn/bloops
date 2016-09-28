from stream import create_stream, transposed, SampleBuffer

def playback(stream, queue):
	while True:
		stream.write(queue.get())

class Emitter(object):
	def __init__(self, settings, device):
		self.buffer = SampleBuffer()
		self.stream = create_stream(
			settings=settings,
			device=device,
			output=True,
			callback=lambda *args: self.playback(*args)
		)

	def playback(self, output, *rest):
		# Get transposed version because sounddevice expects transposed shape
		# relative to what the rest of the system uses, e.g. (len, channels)
		# instead of (channels, len).
		output[:] = transposed(self.buffer.get_samples(*output.shape))

	def emit(self, arr):
		self.buffer.put(arr)

	def start(self):
		self.stream.start()

	def stop(self):
		self.stream.stop()