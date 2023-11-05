import time
import threading

import alsaaudio as aa
import numpy as np

import test

from config import *
from stream import *
from data import *
from gpio import *
from pulse import *

from util import handle_close

print(aa.pcms())
handle_close()

dac = AudioDevice("dac", 192000)
output = Stream(dac, False, False)

# ultramics = Device('ultramics', 192000)
# input = Recorder(ultramics)

click = Chirp(3e4, 1e4, 1e3)

while True:
    with emitter_enable:
        time.sleep(1)
        output.write_array(click.render(dac))
