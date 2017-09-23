class NoiseReduceSettings(object):
	def __init__(
		self,
		rate=192000,
		noise_gain=-12.0,
		sensitivity=6.0,
		window_size=512,
		window_step=128,
		spectrum_median_window=1,
		freq_smoothing_bins=0,
		attack_time=0.05,
		attack_lookback_steps=20,
		release_time=0.05,
		double_window=True
	):
		self.rate = rate
		self.noise_gain = noise_gain
		self.sensitivity = sensitivity
		self.window_size = window_size
		self.window_step = window_step
		self.spectrum_median_window = spectrum_median_window
		self.freq_smoothing_bins = freq_smoothing_bins
		self.attack_time = attack_time
		self.attack_lookback_steps = attack_lookback_steps
		self.release_time = release_time
		self.double_window = double_window


