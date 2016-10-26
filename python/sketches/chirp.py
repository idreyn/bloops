import time
import sys

import sketch
from config import *
from emit import *
from pulse import *
from record import *

from process import EnvironmentSample
from util import handle_close, resample

import numpy as np

handle_close()

try:
    output = choose_output()
    input = choose_input()
except:
    sys.exit(0)

output.rate = 192000

print output.name
print input.name

settings = Settings(
    output_device=output,
    input_device=input
)

e = Emitter(settings)
r = Recorder(settings)

CLICK = 30000
LOW = 20000
HIGH = 60000
LENGTH = 1.5e4
SLEEP_BEFORE = 5e3
DURATION = 2e5
STRETCH = 10

tone_down = Chirp(settings, HIGH, LOW, LENGTH)
tone_up = Chirp(settings, LOW, HIGH, LENGTH)
click_test = Tone(settings, CLICK, 1e3)

def chirp_once(up=False, click=False):
    print "chirp!"
    e.start()
    r.buffer.empty()
    r.start()
    time.sleep(SLEEP_BEFORE / 1e6)
    e.emit((
        click_test if click 
        else (tone_up if up else tone_down)
    ).render())
    time.sleep(DURATION / 1e6)
    r.stop()
    samples = r.buffer.get_samples()
    try:
        sample = EnvironmentSample(
            samples,
            input.rate,
            SLEEP_BEFORE
        ).process()
    except:
        return
    sample = np.repeat(sample, STRETCH, axis=0)
    e.emit(sample)
    time.sleep((STRETCH * (DURATION + SLEEP_BEFORE)) * 1e-6)
    time.sleep(0.5)

if __name__ == "__main__":
    while True:
        chirp_once()
