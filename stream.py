from __future__ import division

import numpy as np
import alsaaudio as aa
import time
import threading

from data import *

class Stream(object):
    def __init__(self, device, is_input, is_blocking=True):
        self.pcm = None
        self.device = device
        self.is_input = is_input
        self.is_blocking = is_blocking
        self.setup()

    def setup(self):
        if self.pcm:
            self.pcm.close()
        self.pcm = aa.PCM(
            type=aa.PCM_CAPTURE if self.is_input else aa.PCM_PLAYBACK,
            mode=aa.PCM_NORMAL if self.is_blocking else aa.PCM_NONBLOCK,
            device=self.device.name,
        )
        self.pcm.setrate(self.device.rate)
        self.pcm.setchannels(self.device.channels)
        self.pcm.setformat(self.device.format)
        self.pcm.setperiodsize(self.device.period_size)
        self._okay = True
        self._paused = False

    def pause(self):
        if not self._paused:
            self._paused = True
            self.pcm.pause(True)

    def resume(self):
        if self._paused:
            self._paused = False
            self.pcm.pause(False)

    def read(self):
        length, data = self.pcm.read()
        if length < 0:
            self._okay = False
            raise Exception("Error reading from ALSA stream: %s" % length)
        return data

    def write(self, bytes):
        self.pcm.write(bytes)

    def write_array(self, array):
        device = self.device
        periods = array_to_periods(array, device)
        for p in periods:
            self.write(p)

    def read_array(self, n_samples):
        period_count = n_samples // self.device.period_size
        samples = []
        while len(samples) < period_count:
            samples.append(self.read())
        return periods_to_array(samples, self.device)
