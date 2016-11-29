from __future__ import division

import numpy as np
import alsaaudio as aa
import time

from data import *

class Stream(object):

    def __init__(self, device, is_input):
        self.device = device
        self.is_input = is_input
        self.pcm = aa.PCM(
            type=aa.PCM_CAPTURE if is_input else aa.PCM_PLAYBACK,
            mode=aa.PCM_NORMAL,
            device=self.device.name
        )
        self.pcm.setrate(device.rate)
        self.pcm.setchannels(device.channels)
        self.pcm.setformat(aa.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(device.period_size)

    def __enter__(self, *rest):
        pass

    def __exit__(self, *rest):
        pass

    def read(self):
        length, data = self.pcm.read()
        return data

    def write(self, bytes):
        self.pcm.write(bytes)

    def write_array(self, array):
        period = self.device.period
        periods = array_to_periods(
            pad(
                array,
                period,
                0
            ),
            self.device
        )
        with self as stream:
            for p in periods:
                stream.write(p)

    def read_array(self, seconds):
        period_count = (self.device.rate // self.device.period_size) * seconds
        samples = []
        with self as stream:
            while len(samples) < period_count:
                samples.append(self.read())
        print len(samples), len(samples[0])
        return periods_to_array(samples, self.device)