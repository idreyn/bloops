import time
import traceback
import sounddevice as sd

from stream import *
from record import *
from config import *
from util import *

class Audio(object):

    def __init__(self, record_device, emit_device, playback_device=None):
        self.record_device = record_device
        self.emit_device = emit_device
        self.playback_device = playback_device or emit_device
        self.recorder = None
        self.emit_stream = None
        self.playback_stream = None

    # Either returns the objects you need to echolocation
    # or returns False if they're not available
    def io(self):
        if not self.recorder:
            try:
                self.recorder = Recorder(self.record_device)
            except Exception as e:
                return False
        else:
            if not self.recorder.assert_okay():
                self.recorder.close()
                self.recorder = None
                return False
        if not self.emit_stream:
            try:
                self.emit_device.check_settings(False)
                self.emit_stream = Stream(self.emit_device, False, False)
            except Exception as e:
                return False
        else:
            if not self.emit_stream.assert_okay():
                self.emit_stream.close()
                self.emit_stream = None
                return False
        if not self.playback_stream:
            if self.playback_device != self.emit_device:
                try:
                    self.playback_device.check_settings(False)
                    self.playback_stream = Stream(
                        self.playback_device, False, False)
                except:
                    return False
            else:
                self.playback_stream = self.emit_stream
        else:
            if not self.playback_stream.assert_okay():
                self.playback_stream.close()
                self.playback_stream = None
                return False
        return (self.recorder, self.emit_stream, self.playback_stream)

    def await_available(self):
        while not self.io():
            time.sleep(0.00001)

    def await_unavailable(self):
        while self.io():
            time.sleep(0.00001)


