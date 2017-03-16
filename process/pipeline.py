from sample import EnvironmentSample, ChannelSample
from stages import *


class Pipeline(object):

    def __init__(self, steps):
        for s in steps:
            try:
                s.__stage__
            except:
                raise Exception(
                    "%s is not a valid pipeline stage because it was not" +
                    " decorated with the @stage decorator" % (s.__name__)
                )
        self.steps = steps

    def run(self, echolocation, sample):
        if sample.shape[1] != 2:
            raise Exception("Pipeline only supports 2-channel audio for now.")
        pulse = echolocation.pulse
        es = EnvironmentSample(
            sample=sample,
            rate=pulse.device.rate,
            us_pulse_duration=pulse.us_duration,
            hz_band=pulse.band(),
            np_format=pulse.device.np_format
        )
        for step in self.steps:
            es = step(es)
        return es.render()

STANDARD_PIPELINE = Pipeline((
    align_samples,
    split_silence,
    detrend,
    bandpass,
    noisereduce
))
