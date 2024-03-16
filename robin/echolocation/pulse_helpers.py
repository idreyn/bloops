from .pulse import Tone, Chirp, Noise


def tone(khz_freq: int, ms_duration: int):
    return Tone(ms_duration=ms_duration, khz_freq=khz_freq)


def chirp(khz_start: int, khz_end: int, ms_duration: int):
    return Chirp(ms_duration=ms_duration, khz_start=khz_start, khz_end=khz_end)


def noise(ms_duration: int):
    return Noise(ms_duration=ms_duration)
