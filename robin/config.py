"""
   ___  ____  ___  _____  __
  / _ \/ __ \/ _ )/  _/ |/ /
 / , _/ /_/ / _  |/ //    / 
/_/|_|\____/____/___/_/|_/  
Echolocation for everyone

"""

import alsaaudio as aa
import numpy as np

BATCAVE_HOST = ('128.31.37.145', 8000)
DEVICE_ID = 'robin-prototype'

CHANNELS = 2
FORMAT = aa.PCM_FORMAT_S16_LE
PERIOD_SIZE = 1000
RATE = 192000

def format_size(format):
    return {
        aa.PCM_FORMAT_S16_LE : 2,
        aa.PCM_FORMAT_S24_LE: 3,
        aa.PCM_FORMAT_FLOAT_LE: 4
    }.get(format)

def format_np(format):
    return {
        aa.PCM_FORMAT_S16_LE: np.int16,
        aa.PCM_FORMAT_FLOAT_LE: np.float32
    }.get(format)
