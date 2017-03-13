"""
   ___  ____  ___  _____  __
  / _ \/ __ \/ _ )/  _/ |/ /
 / , _/ /_/ / _  |/ //    / 
/_/|_|\____/____/___/_/|_/  
Echolocation for everyone

"""
import time
from shutil import copyfile
from os import path

import alsaaudio as aa
import sounddevice as sd
import numpy as np

from util import get_ip_address

BASE_PATH = path.abspath(path.dirname(__file__))

BATCAVE_HOST = ('128.31.37.145', 8000)
DEVICE_ID = 'robin-prototype'
IP = get_ip_address()

CHANNELS = 2
FORMAT = aa.PCM_FORMAT_S16_LE
PERIOD_SIZE = 1000
RATE = 192000

# Format fun

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

class AudioDevice(object):
    
    def __init__(self, name, rate=RATE, channels=CHANNELS, 
            format=FORMAT, period_size=PERIOD_SIZE):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size

    def period_length(self):
        return float(self.period_size) / self.rate

    def check_settings(self, as_input=True):
        (sd.check_input_settings if as_input else sd.check_output_settings)(
            device=self.name,
            channels=self.channels,
            samplerate=self.rate,
            dtype=self.np_format
        )

ULTRAMICS = AudioDevice('ultramics', 200000, 2)
DAC = AudioDevice('snd_rpi_hifiberry_dacplus', 192000, 2)
REQUIRED_INPUT_DEVICES = [ULTRAMICS]
REQUIRED_OUTPUT_DEVICES = [DAC]

print "BASE_PATH", BASE_PATH

def has_needed_devices():
    try:
        [d.check_settings() for d in REQUIRED_INPUT_DEVICES]
        [d.check_settings(False) for d in REQUIRED_OUTPUT_DEVICES]
        return True
    except:
        return False

def setup_asoundrc():
    global sd
    config_dir = BASE_PATH + '/../config/'
    if has_needed_devices():
        return
    copyfile(config_dir + 'asound.conf-a', path.expanduser('~/.asoundrc'))
    time.sleep(1)
    import sounddevice as sd
    if has_needed_devices():
        return
    copyfile(config_dir + 'asound.conf-b', path.expanduser('~/.asoundrc'))
    time.sleep(1)
    import sounddevice as sd
    if has_needed_devices():
        return
    else:
        raise Exception("Missing audio hardware")



