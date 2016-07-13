import time

import numpy as np

from config import *
from data import *
from emit import *
from pulse import *

audio = PA()
output_device_index, output_device = choose_output(audio)
settings = Settings(device=output_device, np_format=np.float32)

emit = Emitter(audio, settings)
tone = Chirp(settings, 1000, 5000, 1e5)

emit.play(tone.render())

time.sleep(2)