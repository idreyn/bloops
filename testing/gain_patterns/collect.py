import time
import sys
import numpy as np
from typing import List

from robin.audio import Audio
from robin.config import BATHAT, ULTRAMIC
from robin.gpio import emitter_enable
from robin.pulse import Tone
from robin.wav import save_wav_file

from .models import Experiment, ExperimentEntry

audio = Audio(emit_device=BATHAT, record_device=ULTRAMIC)
audio.start(record_capacity_periods=2000)


def get_tone_ladder_recording(frequencies: List[int], tone_length: int):
    tones = [Tone(freq, tone_length).render(BATHAT) for freq in frequencies]
    start_time = time.time()
    with emitter_enable:
        for tone in tones:
            audio.add_to_emit(tone)
            time.sleep(0.1)
    end_time = time.time()
    recording = audio.record_buffer.get_for_interval(start_time, end_time)
    return recording.astype(np.int16)


def collect_trial_entry(entry: ExperimentEntry):
    recording = get_tone_ladder_recording(
        entry.experiment.frequencies,
        entry.experiment.tone_length_us,
    )
    save_wav_file(recording, ULTRAMIC.rate, entry.wav_file_path)


def collect_experiment(exp: Experiment):
    try:
        for azimuth in exp.azimuths:
            for trial in range(exp.trials_per_azimuth):
                entry = ExperimentEntry(exp, azimuth, trial)
                if entry.wav_file_exists:
                    continue
                print(f"Press [enter] to collect azimuth={azimuth}, trial={trial}", end="")
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
        name="testing",
        min_freq=20000,
        max_freq=50000,
        freq_spacing=2500,
        tone_length_us=2e4,
    )
    collect_experiment(exp)