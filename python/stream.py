import numpy as np
import alsaaudio as aa
import time

class Stream(object):
    def __init__(self, device, is_input):
        self.device = device
        self.is_input = is_input
        self.pcm = aa.PCM(
            type=aa.PCM_CAPTURE, #if is_input else aa.PCM_PLAYBACK,
            mode=aa.PCM_NORMAL,
            device=self.device.name
        )
        self.pcm.setrate(200000)
        self.pcm.setchannels(2)
        self.pcm.setformat(aa.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(1) 
        while True:
          print self.read()

    def read(self):
      return np.fromstring(
          self.pcm.read(),
          dtype=self.settings.format
      )

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
                            return buff
