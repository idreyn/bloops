from __future__ import division
import test, time

import numpy as np
from scikits.audiolab import *
import matplotlib.pyplot as plt

from util import bandpass

def save(filename, data, rate):
    f = Sndfile(filename, 'w', Format('wav'), 1, rate)
    f.write_frames(data)
    f.close()

hz_bottom_freq = 2e4
hz_bandwidth = 3e4

sample, hz_rate, fmt = wavread("../../samples/heterodyne-pre.wav")
left = sample[:, 0]

t = np.linspace(start=0, stop=(len(sample) / hz_rate), num=len(sample))
x = np.sin(2 * np.pi * t * hz_bottom_freq)
signal = bandpass(x * left, 0, hz_bandwidth, hz_rate)

plt.specgram(signal, Fs=hz_rate)
plt.show()

save('../../samples/heterodyne-post.wav', signal, hz_rate)
