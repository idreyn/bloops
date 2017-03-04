import time
import bisect
import numpy as np


class SampleBuffer(object):

    def __init__(self, channels, capacity=500):
        self.queue = []
        self.times = []
        self.channels = channels
        self.capacity = capacity

    def time_range(self):
        return (self.times[0], self.times[-1])

    def put(self, sample):
        self.queue.append(np.copy(sample))
        self.times.append(time.time())
        if len(self.queue) > self.capacity:
            self.shift()

    def shift(self, ln=1):
        self.queue = self.queue[ln:]
        self.times = self.times[ln:]

    def pointer_for_time(self, time, start_limit=0, end_limit=None):
        if not end_limit:
            end_limit = len(self.times)
        midpoint = (start_limit + end_limit) / 2

    def get_samples(self, length, start_time=None):
        offset = 0 if start_time is None \
            else bisect.bisect_left(self.times, start_time)
        self.shift(offset)
        pointer = 0
        buff = np.zeros((length, self.channels))
        while pointer < length:
            if not len(self.queue):
                print "underflow", pointer
                break
            else:
                sample = self.queue[0]
                take = min(length - pointer, len(sample))
                buff[pointer: pointer + take, :] = sample[0:take, :]
                self.queue[0] = sample[take:, :]
                pointer = pointer + take
                if not len(self.queue[0]):
                	self.shift()
        return buff
