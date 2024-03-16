import numpy as np


class ChannelSample(object):
    def __init__(self, sample, silence_boundary_index):
        self.sample = sample
        self.signal = sample  # sample[silence_boundary_index:]
        self.silence = sample[0:silence_boundary_index]
        self.pulse_start_index = None
        self.pulse_start_offset = None


class EnvironmentSample(object):
    def __init__(
        self,
        sample,
        rate,
        ms_silence_before,
        ms_pulse_duration,
        hz_band=None,
        ms_expected_distance=np.inf,
        np_format=np.int16,
    ):
        self.rate = rate
        self.ms_pulse_duration = ms_pulse_duration
        self.ms_expected_distance = ms_expected_distance
        self.ms_silence_before = ms_silence_before
        self.silence_boundary_index = int(1e-3 * ms_silence_before * self.rate) // 10
        self.ms_record_duration = 1e3 * len(sample) / self.rate
        self.hz_band = hz_band or (0, self.rate / 2)
        self.np_format = np_format
        self.stages = []
        self.channels = [
            ChannelSample(sample[:, 0], self.silence_boundary_index),
            ChannelSample(sample[:, 1], self.silence_boundary_index),
        ]

    def passed_stages(self, stages):
        return set(self.stages) >= set(stages)

    def pass_stage(self, stage):
        self.stages.append(stage)

    def render(self):
        res = np.empty(
            (len(self.channels[0].signal), len(self.channels)), dtype=self.np_format
        )
        for i, c in enumerate(self.channels):
            res[:, i] = c.signal
        return res
