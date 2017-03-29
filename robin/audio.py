import time
import traceback
import threading
import sounddevice as sd

from stream import *
from record import *
from config import *
from util import *
from samplebuffer import *

def run_emit_thread(emit_stream, buffers):
    period_size = emit_stream.device.period_size
    """
    while True:
        emit_stream.write_array(reduce(
            np.add,
            [b.get_samples(period_size) for b in buffers]
        ))
    """

def run_record_thread(record_stream, record_buffer):
    period_size = record_stream.device.period_size
    while True:
        arr = record_stream.read_array(period_size)
        t0 = time.time()
        record_buffer.put_samples(arr)
        print "put samples took", time.time() - t0
        print record_buffer.time_range()
    
class Audio(object):

    def __init__(self, record_device, emit_device):
        self.s_record_buffer_size = 5
        self.s_emit_buffer_size = 5
        self.record_device = record_device
        self.emit_device = emit_device
        self.record_stream = None
        self.emit_stream = None
        self.record_buffer = SampleBuffer(
            (
                int(self.record_device.rate * self.s_record_buffer_size), 
                self.record_device.channels
            ),
            self.record_device.rate
        )
        self.emit_buffer = SampleBuffer(
            (
                int(self.emit_device.rate * self.s_emit_buffer_size), 
                self.emit_device.channels
            ),
            self.emit_device.rate
        )

    def start(self):
        self.emit_stream = Stream(self.emit_device, False)
        self.record_stream = Stream(self.record_device, True)
        self.emit_thread = threading.Thread(target=run_emit_thread,
            args=(self.emit_stream, [self.emit_buffer]))
        self.emit_thread.daemon = True
        self.emit_thread.start()
        self.record_thread = threading.Thread(target=run_record_thread,
            args=(self.record_stream, self.record_buffer))
        self.record_thread.daemon = True
        self.record_thread.start()
