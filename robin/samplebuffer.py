from __future__ import division

import time
import threading
import collections
import bisect
import numpy as np

class SampleBuffer(object):

    def __init__(self, shape, rate):
        self.shape = shape
        self.length = shape[0]
        self.channels = shape[1]
        self.rate = rate
        self.times = collections.deque([]) # List of insert times
        self.time_indices = {} # Map timestamps to buffer indices
        self.lock = threading.Lock()
        self.buffer = np.zeros(shape)
        self.latest_nonzero_index = -1
        self._empty = None

    def time_range(self):
        return (self.times[0], self.times[-1])

    def put_samples(self, sample):
        assert sample.shape[0] <= self.length
        assert sample.shape[1] == self.channels
        now = time.time()
        self.lock.acquire()
        if self.latest_nonzero_index + len(sample) > self.length:
            # Roll as many items through the list as we need to do insert
            roll = (self.latest_nonzero_index + len(sample)) - self.length + 1
            t0 = time.time()
            self.buffer = np.roll(self.buffer, -roll)
            print "roll operation took", time.time() - t0
            self.latest_nonzero_index = self.length - roll - 1
            t0 = time.time()
            for t in list(self.times):
                self.time_indices[t] -= roll
                if self.time_indices[t] < 0:
                    del self.time_indices[t]
                    self.times.popleft()
        insert_index = self.latest_nonzero_index + 1
        self.time_indices[now] = insert_index
        self.times.append(now)
        print insert_index, len(sample)
        self.buffer[insert_index:insert_index+len(sample)] = sample
        self.latest_nonzero_index += len(sample)
        self.lock.release()

    def set_empty(self, sample):
        self._empty = sample

    def get_samples(self, length, start_time=None):
        if len(self.queue) == 0 and not self._empty is None:
            self.queue.append(self._empty)
        offset = 0 if start_time is None \
            else bisect.bisect_left(self.times, start_time)
        if offset > 0:
            self._shift(offset)
        pointer = 0
        buff = np.zeros((length, self.channels))
        i = 0
        while pointer < length:
            i = i + 1
            if not len(self.queue):
                break
            else:
                sample = self.queue[0]
                take = min(length - pointer, len(sample))
                buff[pointer: pointer + take, :] = sample[0:take, :]
                self.queue[0] = sample[take:, :]
                pointer = pointer + take
                if not len(self.queue[0]):
                    self._shift()
        print "iterations", i
        return buff
