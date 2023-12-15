import time
from datetime import datetime
from os import path, mkdir

from robin.constants import BASE_PATH
from robin.profile import Profile
from robin.util.wav import save_wav_file


def now_stamps():
    t0 = time.time()
    dt = datetime.fromtimestamp(t0)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d-%H-%M-%S")


class EcholocationCapture(object):
    def __init__(
        self,
        pulse,
        slowdown,
        device,
        us_record_duration=1e5,
        us_silence_before=1e4,
    ):
        self.pulse = pulse
        self.slowdown = slowdown
        self.device = device
        self.us_silence_before = us_silence_before
        self.us_record_duration = us_record_duration
        self.recording = None
        self.resampled = None
        self.camera_image = None

    def save_echolocation_capture(self, profile: Profile):
        datestamp, timestamp = now_stamps()
        fs = self.device.rate
        base = f"{profile.save_prefix()}{timestamp}__{self.pulse}"
        recordings_dir = base_filename = path.join(BASE_PATH, "..", "recordings")
        if not path.exists(recordings_dir):
            mkdir(recordings_dir)
        base_dir = path.join(recordings_dir, datestamp)
        if not path.exists(base_dir):
            mkdir(base_dir)
        base_filename = path.join(base_dir, base)
        if profile.should_play_recording():
            save_wav_file(f"{base_filename}.wav", self.recording, fs)
        if profile.should_save_resampled():
            save_wav_file(f"{base_filename}__resampled.wav", self.resampled, fs)
        if profile.should_save_pulse():
            save_wav_file(f"{base_filename}__pulse.wav", self.pulse, fs)
        if profile.should_save_camera_image() and self.camera_image:
            self.camera_image.save_to_file(f"{base_filename}__capture.png")
