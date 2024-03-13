import time
import threading
import bisect
import numpy as np


class SampleBuffer(object):
    def __init__(self, channels, rate, capacity=500):
        self.channels = channels
        self.rate = rate
        self.capacity = capacity
        self.lock = threading.Lock()
        self.queue = []
        self.times = []
        self.flag_when_removed = None
        self.flagged_and_removed = None
        self.flagged_remove_time = None
        self._empty = None

    def _shift(self, ln=1):
        res = self.queue[0:ln]
        self.queue = self.queue[ln:]
        self.times = self.times[ln:]
        return res

    def clear(self):
        self.lock.acquire()
        self.queue = []
        self.times = []
        self.lock.release()

    def time_range(self):
        return (self.times[0], self.times[-1])

    def get_flagged_remove_time(self):
        if not self.flagged_remove_time:
            if self.flag_when_removed:
                raise Exception("Flagged sample not yet removed from buffer")
            else:
                raise Exception("No sample flagged for removal")
        res = self.flagged_remove_time
        self.flagged_remove_time = None
        self.flagged_and_removed = None
        return res

    def put(self, sample, critical=True, flag_removed=False):
        available = self.lock.acquire(critical)
        if not available:
            print("Warning: discarded sample")
            # Toss these samples, we're doing something else
            return
        if flag_removed:
            if self.flag_when_removed:
                print("Warning: overriding buffer's flag_when_removed")
            self.flag_when_removed = sample
        self.queue.append(sample)
        self.times.append(time.time())
        while len(self.queue) > self.capacity:
            self._shift()
        self.lock.release()

    def set_empty(self, sample):
        self._empty = sample

    def get_next(self):
        while len(self.queue) == 0:
            time.sleep(0.001)
        return self.get(len(self.queue[0]))

    def get(self, length, start_time=None, verbose=False, block=False):
        self.lock.acquire()
        if len(self.queue) == 0 and not self._empty is None:  # noqa: E714
            self.queue.append(self._empty)
        offset = 0 if start_time is None else bisect.bisect_left(self.times, start_time)
        self._shift(offset)
        if verbose and start_time:
            print("requested start time", start_time)
            print("bisect found offset", offset)
            print("min/max times", min(self.times), max(self.times))
            print("actual start time", self.times[0])
        mark_as_removed = None
        pointer = 0
        buff = np.zeros((length, self.channels))
        self.lock.release()
        while pointer < length:
            if not len(self.queue):
                if block:
                    continue
                else:
                    break
            else:
                self.lock.acquire()
                sample = self.queue[0]
                if self.flag_when_removed is sample:
                    mark_as_removed = (sample, pointer)
                take = min(length - pointer, len(sample))
                buff[pointer : pointer + take, :] = sample[0:take, :]
                self.queue[0] = sample[take:, :]
                pointer = pointer + take
                if not len(self.queue[0]):
                    self._shift()
                self.lock.release()
        # roughly speaking, expect to be off by a small constant factor
        remove_time = time.time()
        if mark_as_removed:
            (sample, offset) = mark_as_removed
            self.flag_when_removed = None
            self.flagged_and_removed = sample
            self.flagged_remove_time = remove_time + (offset / self.rate)
        return buff

    def get_for_interval(self, start_time_s, end_time_s, verbose=False):
        samples = int(self.rate * (end_time_s - start_time_s))
        return self.get(length=samples, start_time=start_time_s, verbose=verbose)
