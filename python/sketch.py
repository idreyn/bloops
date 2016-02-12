import pyaudio
import time

import numpy as np
import matplotlib.pyplot as plt

from scikits.audiolab import *

from config import *
from emit import *
from record import *
from process import *
from util import *
from frames import *

audio = pyaudio.PyAudio()

microphones = choose_microphone(audio)
if microphones is None:
	log_fail("Unable to detect ultramics")
rec = Recorder(audio,input_device_index=microphones.get('index'))

frames = rec.record(3)
data = frames_to_array(frames)
play_frames(audio,frames,1)
