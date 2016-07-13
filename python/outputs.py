import pyaudio

from scikits.audiolab import play
from scipy.fftpack import fft

from plotting.util import * 

from emit import *
from config import *
from frames import *

audio = pyaudio.PyAudio()
emit = Emitter(audio)

tone = Tone(343,1e6)
chirp = Chirp(1000,10000,1e4,'linear',square=True)
click = Click(5e3,1000,10000)

play(np.concatenate((chirp.render(),np.zeros(1e5))))
