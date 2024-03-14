from typing import List
import alsaaudio as aa

from robin.io.audio import AudioDevice

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

HIFIBERRY = AudioDevice(
    name="sndrpihifiberry",
    rate=RATE,
    channels=CHANNELS,
    format=FORMAT,
    period_size=PERIOD_SIZE,
)

HEADPHONES = AudioDevice(
    name="Headphones",
    rate=RATE,
    channels=CHANNELS,
    format=FORMAT,
    period_size=PERIOD_SIZE,
)

NULL = AudioDevice(
    is_null_device=True,
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


def pick_available_device(devices: List[AudioDevice]):
    return next(device for device in devices if device.available(as_input=True))
