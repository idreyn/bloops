import time

from scikits.audiolab import wavread
import matplotlib.pyplot as plt

from process import *
from wav import *
from util import *

audio = pyaudio.PyAudio()
sample, sample_freq, encoding = wavread('../sounds/single-bloop.wav')
prep_for_playback(sample)