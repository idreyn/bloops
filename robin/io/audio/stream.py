from queue import Queue
import time
import threading
import sounddevice as sd

from .stream import *
from .util import *
from .samplebuffer import *

def run_emit_or_playback_thread(emit_stream, emit_queue):
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
            print(e)
            record_stream.setup()


def format_size(fmt):
    return {
        aa.PCM_FORMAT_S16_LE: 2,
        aa.PCM_FORMAT_S24_LE: 3,
        aa.PCM_FORMAT_FLOAT_LE: 4,
    }.get(fmt)


def format_np(fmt):
    return {aa.PCM_FORMAT_S16_LE: np.int16, aa.PCM_FORMAT_FLOAT_LE: np.float32}.get(fmt)


class AudioDevice(object):
    def __init__(
        self,
        name,
        rate: float,
        channels: int,
        format: str,
        period_size: int,
        unmute_on_startup=False,
    ):
        self.name = name
        self.channels = channels
        self.rate = rate
        self.format = format
        self.period_size = period_size
        self.width = format_size(format)
        self.np_format = format_np(format)
        if unmute_on_startup:
            self.unmute_and_set_volume()

    def unmute_and_set_volume(self):
        mixer = aa.Mixer(device=f"hw:CARD={self.name}")
        mixer.setmute(0)
        mixer.setvolume(100)

    def frame_bytes(self):
        return self.width * self.channels

    def period_bytes(self):
        return self.frame_bytes() * self.period_size

    def period_length(self):
        return float(self.period_size) / self.rate

    def available(self, as_input):
        return True
        try:
            (sd.check_input_settings if as_input else sd.check_output_settings)(
                device=self.name,
                channels=self.channels,
                samplerate=self.rate,
                dtype=self.np_format,
            )
            return True
        except:
            return False


def run_emit_or_playback_thread(emit_stream, emit_queue):
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
