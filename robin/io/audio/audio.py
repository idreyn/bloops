import threading
from queue import Queue

from .samplebuffer import SampleBuffer
from .stream import Stream


def run_emit_or_playback_thread(emit_stream: Stream, emit_queue: Queue):
    while True:
        emit_stream.write_array(emit_queue.get())


def run_record_thread(record_stream: Stream, record_buffer: SampleBuffer):
    period_size = record_stream.device.period_size
    while True:
        try:
            samples = record_stream.read_array(period_size)
            record_buffer.put(samples, False)
        except Exception as e:
            print(e)
            record_stream.setup()


class Audio(object):
    def __init__(self, record_device=None, emit_device=None, playback_device=None):
        self.record_device = record_device
        self.emit_device = emit_device
        self.playback_device = playback_device

    def start(self, record_capacity_periods=500):
        if self.record_device:
            self.record_buffer = SampleBuffer(
                self.record_device.channels,
                self.record_device.rate,
                record_capacity_periods,
            )
            self.record_stream = Stream(self.record_device, True)
            self.record_thread = threading.Thread(
                target=run_record_thread,
                args=(self.record_stream, self.record_buffer),
            )
            self.record_thread.daemon = True
            self.record_thread.start()
        if self.emit_device:
            self.emit_queue = Queue()
            self.emit_stream = Stream(self.emit_device, False)
            self.emit_thread = threading.Thread(
                target=run_emit_or_playback_thread,
                args=(self.emit_stream, self.emit_queue),
            )
            self.emit_thread.daemon = True
            self.emit_thread.start()
        if self.playback_device:
            self.playback_queue = Queue()
            self.playback_stream = Stream(self.playback_device, False)
            self.playback_thread = threading.Thread(
                target=run_emit_or_playback_thread,
                args=(self.playback_stream, self.playback_queue),
            )
            self.playback_thread.daemon = True
            self.playback_thread.start()

    def get_recording(self, *args, **kwargs):
        assert self.record_device, "Record device not specified"
        return self.record_buffer.get(*args, **kwargs)

    def add_to_playback(self, audio):
        assert self.playback_device, "Playback device not specified"
        self.playback_queue.put(audio)

    def add_to_emit(self, audio):
        assert self.emit_device, "Emit device not specified"
        self.emit_queue.put(audio)

    def loopback(self):
        nxt = self.record_buffer.get_next()
        self.playback_queue.put(nxt)
