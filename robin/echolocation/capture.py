import time
from datetime import datetime
from os import path, mkdir

from robin.constants import BASE_PATH
from robin.config import Config
from robin.util.wav import save_wav_file
from robin.io.audio import AudioDevice

from .pulse import Pulse


def now_stamps():
    t0 = time.time()
    dt = datetime.fromtimestamp(t0)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d-%H-%M-%S")


class EcholocationCapture(object):
    def __init__(
        self,
        pulse: Pulse,
        slowdown: int,
        device: AudioDevice,
        ms_record_duration=1e5,
        ms_silence_before=1e4,
    ):
        self.pulse = pulse
        self.slowdown = slowdown
        self.device = device
        self.rendered_pulse = None
        self.ms_silence_before = ms_silence_before
        self.ms_record_duration = ms_record_duration
        self.recording = None
        self.resampled = None
        self.camera_image = None

    def save_echolocation_capture(self, config: Config):
        datestamp, timestamp = now_stamps()
        fs = self.device.rate
        prefix = config.current.save.file_prefix
        base = f"{prefix}{timestamp}__{self.pulse}"
        recordings_dir = base_filename = path.join(BASE_PATH, "..", "recordings")
        if not path.exists(recordings_dir):
            mkdir(recordings_dir)
        base_dir = path.join(recordings_dir, datestamp)
        if not path.exists(base_dir):
            mkdir(base_dir)
        base_filename = path.join(base_dir, base)
        if config.current.save.save_pulse:
            save_wav_file(f"{base_filename}_pulse.wav", self.rendered_pulse, fs)
        if config.current.save.save_recording:
            save_wav_file(f"{base_filename}.wav", self.recording, fs)
        if config.current.save.save_resampled:
            save_wav_file(f"{base_filename}__resampled.wav", self.resampled, fs)
        if config.current.save.save_camera_image and self.camera_image:
            self.camera_image.save_to_file(f"{base_filename}__capture.png")
