import time
import traceback
import sounddevice as sd

from stream import *
from record import *
from config import *
from util import *

class AudioDevice(object):
    
    def __init__(self, name, rate=RATE, channels=CHANNELS, 
            format=FORMAT, period_size=PERIOD_SIZE):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size

    def check_settings(self, as_input=True):
        (sd.check_input_settings if as_input else sd.check_output_settings)(
            device=self.name,
            channels=self.channels,
            samplerate=self.rate,
            dtype=self.np_format
        )

class Audio(object):

    def __init__(self, record_device, emit_device, playback_device=None):
        self.record_device = record_device
        self.emit_device = emit_device
        self.playback_device = playback_device or emit_device
        self.recorder = None
        self.emit_stream = None
        self.playback_stream = None

    def setup_streams(self):
        if self.recorder and self.recorder.assert_okay():
            return True  
        else:
            try:
                self.recorder = Recorder(self.record_device)
                return True
            except Exception as e:
                return False

    def await_available(self):
        while not self.setup_streams():
            time.sleep(0.00001)

    def await_unavailable(self):
        while self.setup_streams():
            time.sleep(0.00001)


