from __future__ import division

import numpy as np
import alsaaudio as aa
import time
import threading

from data import *

class Stream(object):
    def __init__(self, device, is_input, is_blocking=True):
        self.device = device
        self.is_input = is_input
        self.pcm = aa.PCM(
            type=aa.PCM_CAPTURE if is_input else aa.PCM_PLAYBACK,
            mode=aa.PCM_NORMAL if is_blocking else aa.PCM_NONBLOCK,
            device=self.device.name,
        )
        self.pcm.setrate(device.rate)
        self.pcm.setchannels(device.channels)
        self.pcm.setformat(device.format)
        self.pcm.setperiodsize(device.period_size)
        self.lock = threading.Lock()
        self._okay = True
        self._paused = False

    def __enter__(self, *rest):
        self.lock.acquire()
        if self._paused:
            self.pcm.pause(False)

    def __exit__(self, *rest):
        self.lock.release()
        try:
            self.pcm.pause(True)
            self._paused = True
        except:
            pass

    def read(self):
        length, data = self.pcm.read()
        if length <= 0:
            self._okay = False
            raise Exception("Error reading from ALSA stream: %s" % length)
        return data

    def write(self, bytes):
        self.pcm.write(bytes)

    def write_array(self, array):
        device = self.device
        periods = array_to_periods(array, device)
        with self as stream:
            for p in periods:
                self.write(p)

    def assert_okay(self):
        return self._okay

    def close(self):
        self.pcm.close()

    def read_array(self, samples):
        period_count = samples // self.device.period_size
        samples = []
        with self as stream:
            while len(samples) < period_count:
                samples.append(self.read())
        return periods_to_array(samples, self.device)
