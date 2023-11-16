ROBIN = """
   ___  ____  ___  _____  __
  / _ \/ __ \/ _ )/  _/ |/ /
 / , _/ /_/ / _  |/ //    / 
/_/|_|\____/____/___/_/|_/
The wearable echolocator
"""

import sounddevice as sd
import numpy as np
import alsaaudio as aa

import time
import os
import subprocess
from shutil import copyfile

from .util import get_ip_address
from .audio import AudioDevice

# ron paul dot gif
print(ROBIN)

IS_DEVICE = os.environ.get("ROBIN_IS_DEVICE")
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEVICE_ID = os.environ.get("ROBIN_DEVICE_ID")
IP = "robin.local"  # get_ip_address()
BATCAVE_HOST = "http://0.0.0.0:8000"

BLUETOOTH_REMOTE_NAME = "Game-pad"

if not IS_DEVICE:
    print(
        "Notice: not configured as a Robin headset."
        + " Export ROBIN_IS_DEVICE=1 to make that happen."
    )

if not DEVICE_ID:
    default_id = "robin-protoype"
    print("Warning: ROBIN_DEVICE_ID not set. Using %s instead." % (default_id))
    DEVICE_ID = default_id

CHANNELS = 2
PERIOD_SIZE = 1000
RATE = 192000
FORMAT = aa.PCM_FORMAT_S16_LE

BATHAT = AudioDevice(
    name="CS4270",
    rate=RATE,
    channels=CHANNELS,
    format=FORMAT,
    period_size=PERIOD_SIZE,
    unmute_on_startup=True,
)

HEADPHONES = AudioDevice(
    name="Headphones",
    rate=RATE,
    channels=CHANNELS,
    format=FORMAT,
    period_size=PERIOD_SIZE,
)

ULTRAMIC = AudioDevice(
    name="r4",
    rate=RATE,
    channels=1,
    format=FORMAT,
    period_size=PERIOD_SIZE,
)

REQUIRED_INPUT_DEVICES = [BATHAT]
REQUIRED_OUTPUT_DEVICES = [BATHAT, HEADPHONES]


def has_required_devices():
    return (
        len(
            [True for d in REQUIRED_INPUT_DEVICES if not d.available(True)]
            + [True for d in REQUIRED_OUTPUT_DEVICES if not d.available(False)]
        )
        == 0
    )


def print_device_availability():
    print("=== hardware availability ===")
    for d in REQUIRED_OUTPUT_DEVICES:
        print("%s: %s" % (d.name, d.available(False)))
    for d in REQUIRED_INPUT_DEVICES:
        print("%s: %s" % (d.name, d.available(True)))
