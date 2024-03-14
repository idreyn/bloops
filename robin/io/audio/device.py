import alsaaudio as aa

from .formats import format_size, format_np


class AudioDevice(object):
    def __init__(
        self,
        rate: float,
        channels: int,
        format: str,
        period_size: int,
        name: str = None,
        unmute_on_startup=False,
        is_null_device=False,
    ):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)
        self.is_null_device = is_null_device
        if unmute_on_startup:
            self.unmute_and_set_volume()

    def unmute_and_set_volume(self):
        if self.available(as_input=False):
            mixer = aa.Mixer(device=f"hw:CARD={self.name}")
            mixer.setmute(0)
            mixer.setvolume(100)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size

    def period_length(self):
        return float(self.period_size) / self.rate

    def get_pcm(self, as_input, is_blocking=False):
        try:
            device_name = (
                "null" if self.is_null_device else f"hw:CARD={self.name},DEV=0"
            )
            pcm = aa.PCM(
                type=aa.PCM_CAPTURE if as_input else aa.PCM_PLAYBACK,
                mode=aa.PCM_NORMAL if is_blocking else aa.PCM_NONBLOCK,
                format=self.format,
                rate=self.rate,
                device=device_name,
            )
            pcm.setrate(self.rate)
            pcm.setchannels(self.channels)
            pcm.setformat(self.format)
            pcm.setperiodsize(self.period_size)
            return pcm
        except aa.ALSAAudioError:
            return None

    def available(self, as_input):
        maybe_pcm = self.get_pcm(as_input)
        if maybe_pcm:
            maybe_pcm.close()
            return True
        return False
