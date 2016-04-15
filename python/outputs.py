import pyaudio

from scikits.audiolab import play
from scipy.fftpack import fft

from emit import *
from config import *
from frames import *

audio = pyaudio.PyAudio()
emit = Emitter(audio)

tone = Tone(343,1e6)
chirp = Chirp(100,90000,1e5,'logarithmic',square=False)
click = Click(5e3,1000,10000)

play_array(audio,chirp.render())

