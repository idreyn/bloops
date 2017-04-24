from __future__ import division

from Queue import Queue

import time
import traceback
import threading
import sounddevice as sd

from stream import *
from record import *
from config import *
from util import *
from samplebuffer import *

"""
def run_playback_thread(playback_stream, buffers):
    period_size = playback_stream.device.period_size
    while True:
        playback_stream.write_array(reduce(
            np.add,
            [b.get(period_size) for b in buffers]
        ))
"""

def run_emit_thread(emit_stream, emit_queue):
    while True:
        emit_stream.write_array(emit_queue.get())

def run_record_thread(record_stream, record_buffer):
    period_size = record_stream.device.period_size
    period_time = period_size / record_stream.device.rate
    last_record_time = time.time()
    put_duration = 0
    while True:
        try:
            samples = record_stream.read_array(period_size)
            new_record_time = time.time()
            last_record_time = new_record_time
            t0 = time.time()
            record_buffer.put(samples, False)
            put_duration = time.time() - t0
        except Exception as e:
            record_stream.setup()

class Audio(object):

    def __init__(self, record_device, emit_device):
        self.record_device = record_device
        self.emit_device = emit_device
        self.record_stream = None
        self.emit_stream = None
        self.record_buffer = SampleBuffer(
            record_device.channels,
            record_device.rate
        )
        self.emit_queue = Queue()

    def start(self):
        self.emit_stream = Stream(self.emit_device, False)
        self.record_stream = Stream(self.record_device, True)
        self.emit_thread = threading.Thread(target=run_emit_thread,
            args=(self.emit_stream, self.emit_queue))
        self.emit_thread.daemon = True
        self.emit_thread.start()
        self.record_thread = threading.Thread(target=run_record_thread,
            args=(self.record_stream, self.record_buffer))
        self.record_thread.daemon = True
        self.record_thread.start()
