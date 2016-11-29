import numpy as np

class Stream(object):
    def __init__(self, settings, is_input):
        self.settings = settings
        self.is_input = is_input
        self.pcm = aa.PCM(
            

class SampleBuffer(object):
	def __init__(self, channels):
		self.queue = []
                self.channels = channels

        def size(self):
            return sum([len(s) for s in self.queue])

	def put(self, sample):
		self.queue.append(np.copy(sample))

	def has(self):
		return len(self.queue) > 0

	def get_chunk(self):
		return self.queue.pop(0)

        def get_samples(self, length=None):
            pointer = 0
            if length is None:
                length = self.size()
            buff = np.zeros((length, self.channels))
            while pointer < length:
                if not len(self.queue):
                        break
                else:
                    sample = self.queue[0]
                    take = min(length - pointer, len(sample))
                    buff[pointer : pointer + take, :] = sample[0:take, :]
                    self.queue[0] = sample[take:, :]
                    pointer = pointer + take
                    if not len(self.queue[0]):
                            self.queue.pop(0)
                            return buff;:
