from typing import Optional
from queue import Queue
import time
import numpy as np

from robin.io.gpio import emitter_enable
from robin.util.wav import byte_encode_wav_data
from robin.batcave.protocol import Message
from robin.batcave.client import send_to_batcave_remote
from robin.util import zero_pad_to_multiple
from robin.echolocation.capture import EcholocationCapture
from robin.echolocation.pulse import Pulse
from robin.io.audio import Audio
from robin.io.camera import Camera
from robin.pipeline import Pipeline
from robin.profile import Profile


def echolocate(
    pulse: Pulse,
    audio: Audio,
    camera: Camera,
    profile: Profile,
    pipeline: Optional[Pipeline] = None,
):
    ec = EcholocationCapture(
        pulse=pulse,
        slowdown=profile.slowdown,
        device=audio.record_device,
        us_record_duration=profile.us_record_duration,
        us_silence_before=profile.us_silence_before,
    )
    # TODO make gain configurable
    rendered = (1 / 3) * ec.pulse.render(audio.emit_device)
    with emitter_enable:
        time.sleep(0.05)
        audio.record_buffer.clear()
        audio.emit_queue.put(rendered)
        t0 = time.time()
        time.sleep(1e-6 * ec.pulse.us_duration)
        record_time = 1e-6 * (ec.us_record_duration + ec.us_silence_before)
        time.sleep(record_time)
    ec.camera_image = camera.get()
    sample = audio.record_buffer.get(
        int(record_time * audio.record_stream.device.rate),
        t0 - ec.us_silence_before,
    )
    if profile.reverse_channels:
        sample = np.flip(sample, axis=1)
    if pipeline:
        t0 = time.time()
        sample = pipeline.run(ec, sample)
        print("Pipeline ran in", round(time.time() - t0, 3))
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
    if profile.should_play_recording():
        while not buffered.empty():
            audio.playback_queue.put(buffered.get(), False)
    resampled = np.concatenate(chunks)
    send_to_batcave_remote(
        Message.AUDIO,
        {"audio": byte_encode_wav_data(resampled, audio.record_device.rate)},
    )
    if profile.should_play_recording():
        time.sleep(ec.slowdown * record_time)
    else:
        print("Playback disabled in profile")
    ec.recording = sample
    ec.resampled = resampled
    ec.save_echolocation_capture(profile)
    print("Done")
    return ec
