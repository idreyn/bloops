import time
import traceback
import sounddevice as sd

from stream import *
from record import *
from config import *
from util import *

class Audio(object):

    def __init__(self, record_device, emit_device):
        self.record_device = record_device
        self.emit_device = emit_device
        self.record_stream = None
        self.emit_stream = None

    # Either returns the objects you need to do echolocation
    # or returns False if they're not available
    def io(self):
        if not self.record_stream:
            try:
                self.record_stream = Stream(self.record_device, True)
            except Exception as e:
                return False
        else:
            if not self.record_stream.assert_okay():
                self.record_stream.close()
                self.record_stream = None
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
        return (self.record_stream, self.emit_stream)

    def await_available(self):
        while not self.io():
            time.sleep(0.00001)

    def await_unavailable(self):
        while self.io():
            time.sleep(0.00001)

    def all_streams(self):
        return set([
            self.record_stream,
            self.emit_stream,
        ])

    def __enter__(self):
        return self.io()


    def __exit__(self, *rest):
        # Kludge o'clock
        self.record_stream.close()
        self.emit_stream.close()
        self.record_stream = None
        self.emit_stream = None


