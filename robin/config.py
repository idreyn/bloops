ROBIN = """
   ___  ____  ___  _____  __
  / _ \/ __ \/ _ )/  _/ |/ /
 / , _/ /_/ / _  |/ //    / 
/_/|_|\____/____/___/_/|_/  
Echolocation for everyone
"""

import sounddevice as sd
import numpy as np

import time
import os
import subprocess
from shutil import copyfile

from util import get_ip_address

# ron paul dot gif
print ROBIN

IS_DEVICE = os.environ.get("ROBIN_IS_DEVICE")
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DEVICE_ID = os.environ.get("ROBIN_DEVICE_ID")
IP = get_ip_address()

BLUETOOTH_REMOTE_NAME = "MOCUTE-032X_B61-2ECF"

if IS_DEVICE:
    import alsaaudio as aa
else:
    print "Notice: not configured as a Robin headset." + \
        " Export ROBIN_IS_DEVICE=1 to make that happen."

    class aa(object):
        PCM_FORMAT_S16_LE = 0
        PCM_FORMAT_S24_LE = 1
        PCM_FORMAT_FLOAT_LE = 2

if not DEVICE_ID:
    default_id = "robin-protoype"
    print "Warning: ROBIN_DEVICE_ID not set. Using %s instead." % (default_id)
    DEVICE_ID = default_id

CHANNELS = 2
PERIOD_SIZE = 1000
RATE = 192000
FORMAT = aa.PCM_FORMAT_S16_LE


def format_size(fmt):
    return {
        aa.PCM_FORMAT_S16_LE: 2,
        aa.PCM_FORMAT_S24_LE: 3,
        aa.PCM_FORMAT_FLOAT_LE: 4
    }.get(fmt)


def format_np(fmt):
    return {
        aa.PCM_FORMAT_S16_LE: np.int16,
        aa.PCM_FORMAT_FLOAT_LE: np.float32
    }.get(fmt)


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

    def available(self, as_input):
        try:
            (sd.check_input_settings
             if as_input
             else sd.check_output_settings
             )(
                device=self.name,
                channels=self.channels,
                samplerate=self.rate,
                dtype=self.np_format)
            return True
        except:
            return False

ULTRAMICS = AudioDevice('ultramics', 200000, 2)
DAC = AudioDevice('dac', 192000, 2)
REQUIRED_INPUT_DEVICES = [ULTRAMICS]
REQUIRED_OUTPUT_DEVICES = [DAC]

def has_required_devices():
    return len(
        [True for d in REQUIRED_INPUT_DEVICES if not d.available(True)] +
        [True for d in REQUIRED_OUTPUT_DEVICES if not d.available(False)]
    ) == 0


def print_device_availability():
    print "=== hardware availability ==="
    for d in REQUIRED_OUTPUT_DEVICES:
        print "%s: %s" % (d.name, d.available(False))
    for d in REQUIRED_INPUT_DEVICES:
        print "%s: %s" % (d.name, d.available(True))


def setup_asoundrc():
    print "setting up .asoundrc"
    # hack hack hack
    asound_conf_file = ("asound.conf-dac-0"
                        if "card 0" in subprocess.check_output(["aplay", "-l"])
                        else "asound.conf-dac-2"
                        )
    copyfile("../config/" + asound_conf_file,
             os.path.expanduser("~/.asoundrc"))

if __name__ == "__main__":
    print "running setup..."
    setup_asoundrc()
