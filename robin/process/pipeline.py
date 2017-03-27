from sample import EnvironmentSample, ChannelSample
from stages import *


class Pipeline(object):

    def __init__(self, steps):
        self.steps = steps

    def run(self, echolocation, sample):
        if sample.shape[1] != 2:
            raise Exception("Pipeline only supports 2-channel audio for now.")
        pulse = echolocation.pulse
        es = EnvironmentSample(
            sample=sample,
            rate=echolocation.device.rate,
            us_pulse_start=0,
            us_pulse_duration=pulse.us_duration,
            hz_band=pulse.band(),
            np_format=echolocation.device.np_format
        )
        for step in self.steps:
            es = step(es)
        return es.render()

STANDARD_PIPELINE = Pipeline([
    split_silence,
    stats,
    normalize_samples,
    align_samples,
    detrend,
    bandpass,
])
