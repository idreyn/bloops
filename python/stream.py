import sounddevice as sd
import numpy as np

def create_stream(settings, output, callback, **kwargs):
    Stream = sd.OutputStream if output else sd.InputStream
    device = settings.output if output else settings.input
    return Stream(
        samplerate=device.rate,
        blocksize=settings.chunk,
        device=device.index,
        channels=device.channels,
        dtype=settings.np_format,
        callback=callback,
        **kwargs
    )

class SampleBuffer(object):
    def __init__(self, channels):
        self.queue = []
        self.channels = channels

    def size(self):
        return sum([len(s) for s in self.queue])

    def put(self, sample):
        self.queue.append(np.copy(sample))

    def empty(self):
        self.queue = []
    
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
