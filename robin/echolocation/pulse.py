import numpy as np
from typing import TYPE_CHECKING
from scipy.signal import chirp
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal

from robin.io.audio import AudioDevice

if TYPE_CHECKING:
    from robin.config import EmitterConfig


class BasePulse(BaseModel):
    ms_duration: int

    def khz_band(self):
        raise NotImplementedError()

    def _render(self):
        raise NotImplementedError()

    def render(self, device: AudioDevice, cfg: "EmitterConfig" = None):
        r = self._render(device)
        if device.channels == 1:
            return r
        else:
            ms_front_delay = cfg.ms_front_delay if cfg else 0
            front_gain = cfg.front_gain if cfg else 1
            side_gain = cfg.side_gain if cfg else 1
            delay = np.zeros(int(1e-3 * ms_front_delay * device.rate)).astype(
                device.np_format
            )
            max_value = np.iinfo(device.np_format).max
            front_channel = front_gain * np.concatenate([delay, r])
            side_channel = side_gain * np.concatenate([r, delay])
            both_channels = np.transpose([front_channel, side_channel])
            res = (max_value * both_channels).astype(device.np_format)
            return res

    def t_axis(self, device: AudioDevice):
        return np.linspace(
            0, 1e-3 * self.ms_duration, int(1e-3 * self.ms_duration * device.rate)
        )


class Chirp(BasePulse):
    kind: Literal["chirp"] = "chirp"
    khz_start: int
    khz_end: int
    logarithmic: bool = False
    square: bool = False

    def khz_band(self):
        return (min(self.khz_start, self.khz_end), max(self.khz_start, self.khz_end))

    @property
    def method(self):
        return "logarithmic" if self.logarithmic else "linear"

    def _render(self, device: AudioDevice):
        times = self.t_axis(device)
        t1 = times[-1]
        res = chirp(
            t=times,
            f0=1e3 * self.khz_start,
            f1=1e3 * self.khz_end,
            t1=t1,
            method=self.method,
        )
        if self.square:
            res[res > 0] = 1
            res[res < 0] = -1
        return res

    def __str__(self):
        return "chirp-%sk-%sk-%sms-%s%s" % (
            str(self.khz_start),
            str(self.khz_end),
            str(self.ms_duration),
            self.method,
            "-square" if self.square else "",
        )


class Tone(BasePulse):
    kind: Literal["tone"] = "tone"
    khz_freq: int
    square: bool = False

    def khz_band(self, khz_leakage=2.5):
        return (self.khz_freq - khz_leakage, self.khz_freq + khz_leakage)

    def _render(self, device: AudioDevice):
        res = np.cos(2 * np.pi * 1e3 * self.khz_freq * self.t_axis(device))
        if self.square:
            res[res > 0] = 1
            res[res < 0] = -1
        return res

    def __str__(self):
        return "tone-%sk-%sms%s" % (
            str(self.khz_freq),
            str(self.ms_duration),
            "-square" if self.square else "",
        )


class Noise(BasePulse):
    kind: Literal["noise"] = "noise"

    def khz_band(self):
        return (15, 90)

    def _render(self, device: AudioDevice):
        return np.random.normal(0, 1, size=len(self.t_axis(device)))

    def __str__(self):
        return f"noise-{self.ms_duration}ms"


Pulse = Annotated[Chirp | Tone | Noise, Field(discriminator="kind")]
