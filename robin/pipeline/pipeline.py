from robin.pipeline.sample import EnvironmentSample
from robin.pipeline.stages import (
    stats,
    skeri_notch,
    bandpass,
    find_pulse_start_index,
    remove_leading_silence,
    attunate_emission,
)


class Pipeline(object):
    def __init__(self, steps):
        self.steps = steps

    def run(self, echolocation, sample, config):
        if sample.shape[1] != 2:
            raise Exception("Pipeline only supports 2-channel audio for now.")
        pulse = echolocation.pulse
        device = echolocation.device
        (khz_low, khz_high) = pulse.khz_band()
        es = EnvironmentSample(
            sample=sample,
            rate=device.rate,
            ms_silence_before=echolocation.ms_silence_before,
            ms_pulse_duration=pulse.ms_duration,
            hz_band=(1e3 * khz_low, 1e3 * khz_high),
            np_format=device.np_format,
        )
        for step in self.steps:
            es = step(es, config)
        return es.render()


STANDARD_PIPELINE = Pipeline(
    [
        stats,
        skeri_notch,
        bandpass,
        find_pulse_start_index,
        remove_leading_silence,
        attunate_emission,
    ]
)
