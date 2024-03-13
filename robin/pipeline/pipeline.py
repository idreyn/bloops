from robin.pipeline.sample import EnvironmentSample
from robin.pipeline.stages import *  # noqa: F403


class Pipeline(object):
    def __init__(self, steps):
        self.steps = steps

    def run(self, echolocation, sample):
        if sample.shape[1] != 2:
            raise Exception("Pipeline only supports 2-channel audio for now.")
        pulse = echolocation.pulse
        device = echolocation.device
        es = EnvironmentSample(
            sample=sample,
            rate=device.rate,
            us_silence_before=echolocation.us_silence_before,
            us_pulse_duration=pulse.us_duration,
            hz_band=pulse.band(),
            np_format=device.np_format,
        )
        for step in self.steps:
            es = step(es)
        return es.render()


STANDARD_PIPELINE = Pipeline(
    [
        stats,  # noqa: F405
        skeri_notch,  # noqa: F405
        # self_notch,
        bandpass,  # noqa: F405
        find_pulse_start_index,  # noqa: F405
        detrend,  # noqa: F405
        noisereduce,  # noqa: F405
        # normalize,
    ]
)
