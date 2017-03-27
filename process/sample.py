import numpy as np

class ChannelSample(object):
	def __init__(
		self,
		sample,
		us_recording_start=0
	):
		self.sample = sample
		self.us_recording_start = us_recording_start
		self.signal = sample # This will likely be altered by a pipeline stage
		self.peak = None
		self.silence = None

class EnvironmentSample(object):
	def __init__(
			self,
			sample,
			rate,
			us_pulse_start,
			hz_band=None,
			us_pulse_duration=None,
			us_expected_distance=np.inf,
			np_format=np.int16
		):
		self.channels = [ChannelSample(sample[:,0]), ChannelSample(sample[:,1])]
		self.rate = rate
		self.us_pulse_duration = us_pulse_duration
		self.us_pulse_start = us_pulse_start
		self.us_expected_distance = us_expected_distance
		self.hz_band = hz_band or (0, self.rate / 2)
		self.np_format = np_format
		self.stages = []

	def passed_stages(self, stages):
		return set(self.stages) >= set(stages)

	def pass_stage(self, stage):
		self.stages.append(stage)		

	def render(self):
		res = np.empty((
			len(self.channels[0].signal),
			len(self.channels)
		), dtype=self.np_format)
		print self.channels[0]
		print self.channels[1]
		for i, c in enumerate(self.channels):
			res[:,i] = c.signal
		return res