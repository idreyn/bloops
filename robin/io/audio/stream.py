import sounddevice as sd

from .stream import *
from .formats import *
from .samplebuffer import *
from .formats import format_size, format_np


class AudioDevice(object):
    def __init__(
        self,
        name,
        rate: float,
        channels: int,
        format: str,
        period_size: int,
        unmute_on_startup=False,
    ):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)
        if unmute_on_startup:
            self.unmute_and_set_volume()

    def unmute_and_set_volume(self):
        mixer = aa.Mixer(device=f"hw:CARD={self.name}")
        mixer.setmute(0)
        mixer.setvolume(100)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size

    def period_length(self):
        return float(self.period_size) / self.rate

    def available(self, as_input):
        try:
            (sd.check_input_settings if as_input else sd.check_output_settings)(
                device=self.name,
                channels=self.channels,
                samplerate=self.rate,
                dtype=self.np_format,
            )
            return True
        except:
            return False
