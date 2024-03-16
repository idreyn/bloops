from typing import Optional
from queue import Queue
import time
import numpy as np

from robin.io.gpio import emitter_enable
from robin.batcave.protocol import Message
from robin.batcave.client import send_to_batcave_remote
from robin.util import zero_pad_to_multiple
from robin.echolocation.capture import EcholocationCapture
from robin.echolocation.pulse import Pulse
from robin.io.audio import Audio
from robin.io.camera import Camera
from robin.pipeline import Pipeline
from robin.config import Config


def echolocate(
    pulse: Pulse,
    audio: Audio,
    camera: Camera,
    config: Config,
    pipeline: Optional[Pipeline] = None,
):
    ec = EcholocationCapture(
        pulse=pulse,
        slowdown=config.current.echolocation.slowdown,
        device=audio.record_device,
        ms_record_duration=config.current.echolocation.ms_record_duration,
        ms_silence_before=config.current.echolocation.ms_silence_before,
    )
    rendered = pulse.render(audio.emit_device, config.current.echolocation.emitters)
    ec.rendered_pulse = rendered
    with emitter_enable:
        time.sleep(1e-3 * config.current.echolocation.emitters.ms_warmup_time)
        audio.record_buffer.clear()
        audio.emit_queue.put(rendered)
        record_time = 1e-3 * (ec.ms_record_duration + ec.ms_silence_before)
        t0 = time.time()
        time.sleep(1e-3 * pulse.ms_duration)
        time.sleep(record_time)
    ec.camera_image = camera.get()
    sample = audio.record_buffer.get(
        int(record_time * audio.record_stream.device.rate),
        t0 - 1e-3 * ec.ms_silence_before,
    )
    if config.current.echolocation.microphones.reverse_channels:
        sample = np.flip(sample, axis=1)
    if pipeline:
        t0 = time.time()
        sample = pipeline.run(ec, sample, config)
        print("Pipeline ran in", round(time.time() - t0, 3))
    send_to_batcave_remote(
        Message.AUDIO,
        {
            "audio": sample.tobytes(),
            "slowdown": ec.slowdown,
            "samplerate": audio.record_device.rate,
        },
    )
    chunks = []
    total_chunks = 10
    buffer_first = 0
    buffered = Queue()
    for i, chunk in enumerate(
        np.split(zero_pad_to_multiple(sample, total_chunks), total_chunks)
    ):
        chunk = np.repeat(chunk, ec.slowdown, axis=0)
        chunks.append(chunk)
        buffered.put(chunk)
        if i >= buffer_first:
            audio.playback_queue.put(buffered.get(), False)
    if config.current.echolocation.playback:
        while not buffered.empty():
            audio.playback_queue.put(buffered.get(), False)
    resampled = np.concatenate(chunks)
    if config.current.echolocation.playback:
        time.sleep(ec.slowdown * record_time)
    else:
        print("Playback disabled in config")
    ec.recording = sample
    ec.resampled = resampled
    ec.save_echolocation_capture(config)
    print("Done")
    return ec
