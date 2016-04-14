import pyaudio

from plotting.util import *

from emit import *
from config import *
from scikits.audiolab import play
from scipy.fftpack import fft

audio = pyaudio.PyAudio()
emit = Emitter(audio)

tone = Tone(300,1e6)
chirp = Chirp(100,10000,1e5,'logarithmic',square=True)
click = Click(5e3,40000,50000)

play(click.render())

