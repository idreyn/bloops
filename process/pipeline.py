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
            us_silence_before=echolocation.us_silence_before,
            us_pulse_duration=pulse.us_duration,
            hz_band=pulse.band(),
            np_format=echolocation.device.np_format
        )
        for step in self.steps:
            es = step(es)
            print es.channels[0].signal.shape, es.channels[1].signal.shape
        return es.render()

STANDARD_PIPELINE = Pipeline([
    bandpass,
    find_pulse_start_index,
    align,
    detrend,
])
