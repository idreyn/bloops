import numpy as np
from scipy.signal import chirp

def pulse_source_from_dict(d):
	def get_from_device(device):
		if d.get("type") == "tone":
			return Tone(
				device,
				1000 * d.get("khzStart"),
				d.get("usDuration"),
				d.get("square")
			)
		elif d.get("type") == "chirp":
			return Chirp(
				device,
				1000 * d.get("khzStart"),
				1000 * d.get("khzEnd"),
				d.get("usDuration"),
				"logarithmic" if d.get("isLogarithmic") else "linear",
				d.get("square")
			)
		elif d.get("type") == "click":
			return Click(
				device,
				d.get("usDuration")
			)
		else:
			raise Exception("Unable to parse Pulse from dict")
	return get_from_device

def default_pulse_source():
	return pulse_source_from_dict({
		'type': 'chirp',
		'usDuration': 5e3,
		'khzStart': 50,
		'khzEnd': 25
	})

class Pulse(object):
	def __init__(self, settings, us_duration, square=False):
		self.us_duration = us_duration
		self.settings = settings
		self.square = square
		self.__t_axis = None
		self.__rendered = None

	def t_axis(self):
		if not self.__t_axis is None:
			return self.__t_axis
		self.__t_axis = np.linspace(
			0,
			1e-6 * self.us_duration,
			1e-6 * self.us_duration * self.settings.rate
		)
		return self.__t_axis

	def render(self):
		if not self.__rendered is None:
			return self.__rendered
		r = self._render()
		if self.square:
			r[r > 0] = 1
			r[r < 0] = -1
		if self.settings.channels == 1:
			self.__rendered = r
		else: 
			self.__rendered = (
				32767 if self.settings.np_format == np.int16 else 1 
			) * np.transpose(np.array(
				[r for _ in xrange(self.settings.channels)]
			))
		return self.__rendered

	def _render(self):
		raise Exception("Pulse should not be instantiated directly")

class Silence(Pulse):
	def __init__(self, device, us_duration):
		super(Silence, self).__init__(device, us_duration)

	def _render(self):
		return np.zeros(len(self.t_axis()))

class Tone(Pulse):
	def __init__(self, device, frequency, us_duration, square=False):
		super(Tone,self).__init__(device, us_duration, square)
		self.frequency = frequency

	def _render(self):
		return np.cos(2 * np.pi * self.frequency * self.t_axis())

class Chirp(Pulse):
	def __init__(self, device, f0, f1, us_duration,
			method='linear', square=False):
		super(Chirp,self).__init__(device, us_duration, square)
		self.f0 = f0
		self.f1 = f1
		self.method = method

	def _render(self):
		times = self.t_axis()
		t1 = times[-1]
		return chirp(
			t=self.t_axis(),
			f0=self.f0,
			f1=self.f1,
			t1=t1,
			method=self.method
		)

class Click(Pulse):
	def __init__(self, device, us_duration):
		super(Click,self).__init__(device, us_duration)

	def _render(self):
		return np.random.normal(0, 1, size=len(self.t_axis()))
