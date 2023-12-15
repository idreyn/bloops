import time
import sys
import numpy as np
from typing import List

from robin.audio import Audio
from robin.config import HIFIBERRY, ULTRAMIC
from robin.gpio import emitter_enable
from robin.pulse import Tone, Silence
from robin.util.wav import save_wav_file

from .models import Experiment, ExperimentEntry

audio = Audio(emit_device=HIFIBERRY, record_device=ULTRAMIC)
audio.start(record_capacity_periods=2000)


def concat_tones(tones, silence):
    interleaved = []
    for array in tones:
        interleaved.append(array)
        interleaved.append(silence.copy())
    interleaved.pop()
    concatenated_array = np.concatenate(interleaved)
    return concatenated_array


def get_tone_ladder_recording(
    frequencies: List[int], tone_length: int, silence_length: int
):
    silence = Silence(silence_length).render(HIFIBERRY)
    tones = [Tone(freq, tone_length).render(HIFIBERRY) for freq in frequencies]
    all_tones = concat_tones(tones, silence)
    import matplotlib.pyplot as plt

    plt.plot(all_tones)
    plt.show()
    start_time = time.time()
    total_time_us = len(frequencies) * (tone_length + silence_length)
    with emitter_enable:
        audio.add_to_emit(all_tones)
        time.sleep(1)
    end_time = time.time()
    recording = audio.record_buffer.get_for_interval(start_time, end_time)
    return recording.astype(np.int16)


def collect_trial_entry(entry: ExperimentEntry):
    recording = get_tone_ladder_recording(
        entry.experiment.frequencies,
        entry.experiment.tone_length_us,
        entry.experiment.silence_length_us,
    )
    save_wav_file(recording, ULTRAMIC.rate, entry.wav_file_path)


def collect_experiment(exp: Experiment):
    try:
        for azimuth in exp.azimuths:
            for trial in range(exp.trials_per_azimuth):
                entry = ExperimentEntry(exp, azimuth, trial)
                if entry.wav_file_exists:
                    continue
                print(
                    f"Press [enter] to collect azimuth={azimuth}, trial={trial}", end=""
                )
                while input("") != "":
                    continue
                collect_trial_entry(entry)
                time.sleep(1)
        print("Done.")
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        exp.save()


if __name__ == "__main__":
    exp = Experiment(
        name="eek",
        min_freq=20000,
        max_freq=50000,
        freq_spacing=2500,
        tone_length_us=1e4,
        silence_length_us=9e4,
    )
    collect_experiment(exp)
