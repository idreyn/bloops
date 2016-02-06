import time

from scikits.audiolab import wavread
import matplotlib.pyplot as plt

from process import *
from wav import *
from util import *

audio = pyaudio.PyAudio()
sample, sample_freq, encoding = wavread('../sounds/single-bloop.wav')
chan = ChannelSample(sample,0)
es = EnvironmentSample(
	[chan,chan],
	55 * 1000,
	5 * 1000
)
res = es.process()
play_array(audio,10 * res,0.02)