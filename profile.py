import json

from remote import RemoteKeys
from pulse import *
from echolocate import *

DEFAULT_REMOTE_MAPPING = {
    RemoteKeys.UP: Chirp(1.5e4, 4e4, 1e3),
    RemoteKeys.DOWN: Chirp(1.5e4, 4e4, 1e4),
    RemoteKeys.LEFT: Chirp(0.5e4, 4e4, 5e3),
    RemoteKeys.RIGHT: Tone(2.5e4, 2e3),
    RemoteKeys.JS_DOWN: Chirp(4e4, 1.5e4, 5e3),
    RemoteKeys.JS_RIGHT: Noise(0.5e3),
}

DEFAULT_SAVE_OPTIONS = {
    'recording': False,
    'resampled': False,
    'pulse': False,
    'prefix': ""
}


class Profile(object):

    def __init__(
            self,
            slowdown=20,
            us_silence_before=6e4,
            us_record_duration=1e5,
            playback=True,
            remote_mapping=DEFAULT_REMOTE_MAPPING,
            save_options=DEFAULT_SAVE_OPTIONS,
            current_pulse=None,
            reverse_channels=False
    ):
        self.slowdown = slowdown
        self.us_silence_before = us_silence_before
        self.us_record_duration = us_record_duration
        self.playback = playback
        self.remote_mapping = remote_mapping
        self.save_options = save_options
        self.current_pulse = current_pulse or Chirp(1.5e4, 4e4, 2.5e3)
        self.reverse_channels = reverse_channels

    def should_play_recording(self):
        return self.playback

    def should_save_recording(self):
        return self.save_options.get("recording")

    def should_save_resampled(self):
        return self.save_options.get("resampled")

    def should_save_pulse(self):
        return self.save_options.get("pulse")

    def save_prefix(self):
        return self.save_options.get("prefix") or ""

    def set_save_all(self, value):
        self.save_options["recording"] = value
        self.save_options["resampled"] = value
        self.save_options["pulse"] = value

    def set_save_prefix(self, value):
        self.save_options["prefix"] = value

    @staticmethod
    def from_file(fn):
        data = json.loads(open(fn, 'r').read())
        print data
        echolocation = data.get('echolocation') or {}
        remote_mapping = data.get('remoteMapping') or {}
        remote_mapping = {
            k: pulse_from_dict(remote_mapping[k])
            for k in remote_mapping
        }
        assert echolocation['slowdown']
        assert echolocation['usRecordDuration']
        assert echolocation['usSilenceBefore']
        assert echolocation['saveOptions']
        assert echolocation['playback']
        return Profile(
            slowdown=echolocation.get('slowdown'),
            us_record_duration=echolocation.get('usRecordDuration'),
            us_silence_before=echolocation.get('usSilenceBefore'),
            save_options=echolocation.get('saveOptions'),
            playback=echolocation.get('playback'),
            remote_mapping=remote_mapping
        )
