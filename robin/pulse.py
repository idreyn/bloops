import numpy as np
from scipy.signal import chirp

from util import zero_pad

def pulse_from_dict(d):
	if d.get("type") == "tone":
		return Tone(
			1000 * d.get("khzStart"),
			d.get("usDuration"),
			d.get("isSquare")
		)
	elif d.get("type") == "chirp":
		return Chirp(
			1000 * d.get("khzStart"),
			1000 * d.get("khzEnd"),
			d.get("usDuration"),
			"logarithmic" if d.get("isLogarithmic") else "linear",
			d.get("isSquare")
		)
	elif d.get("type") == "click":
		return Click(
			d.get("usDuration")
		)
	else:
		raise Exception("Unable to parse Pulse from dict")

def dict_from_pulse(p):
	d = {
		"type": "click" if type(p) is Click else (
			"chirp" if type(p) is Chirp else (
				"tone" if type(p) is Tone else "?"
			)
		),
		"usDuration": p.us_duration
	}
	if type(p) is Tone:
		d["khzStart"] = p.frequency / 1000
		d["isSquare"] = p.square
	elif type(p) is Chirp:
		d["khzStart"] = p.f0 / 1000
		d["khzEnd"] = p.f1 / 1000
		d["isLogarithmic"] = p.method == "logarithmic"
		d["isSquare"] = p.square
	return d

def default_pulse():
	return pulse_from_dict({
		'type': 'chirp',
		'usDuration': 5e3,
		'khzStart': 20,
		'khzEnd': 50,
                'isLogarithmic': True,
	})

class Pulse(object):
	def __init__(self, us_duration, square=False):
		self.us_duration = us_duration
		self.square = square
		self.__t_axis = None
		self.__rendered = None

	def t_axis(self, device):
		if not self.__t_axis is None:
			return self.__t_axis
		self.__t_axis = np.linspace(
			0,
			1e-6 * self.us_duration,
			1e-6 * self.us_duration * device.rate
		)
		return self.__t_axis

	def band(self, device):
		return (0, device.rate / 2)

	def render(self, device):
		if not self.__rendered is None:
			return self.__rendered
		r = self._render(device)
		if self.square:
			r[r > 0] = 1
			r[r < 0] = -1
		if device.channels == 1:
			self.__rendered = r
		else: 
			self.__rendered = (
				32767 if device.np_format == np.int16 else 1 
			) * np.transpose(np.array(
				[r for _ in xrange(device.channels)]
			))
		return self.__rendered

	def _render(self):
		raise Exception("Pulse should not be instantiated directly")

class Silence(Pulse):
	def __init__(self, us_duration):
		super(Silence, self).__init__(us_duration)

	def _render(self, device):
		return np.zeros(len(self.t_axis(device)))

class Tone(Pulse):
	def __init__(self, frequency, us_duration, square=False):
		super(Tone, self).__init__(us_duration, square)
		self.frequency = frequency

	def __str__(self):
		return "tone-%sk-%sms%s" % (
			str(self.frequency / 1000),
			str(self.us_duration / 1000),
			"-square" if self.square else ""
		)

	def _render(self, device):
		return np.cos(2 * np.pi * self.frequency * self.t_axis(device))

	def band(self):
		leakage = 2500 # pretty arbitrary
		return (self.frequency - leakage, self.frequency + leakage)

class Chirp(Pulse):
	def __init__(self, f0, f1, us_duration,
			method='linear', square=False):
		super(Chirp, self).__init__(us_duration, square)
		self.f0 = f0
		self.f1 = f1
		self.method = method

	def __str__(self):
		return "chirp-%sk-%sk-%sms-%s%s" % (
			str(self.f0 / 1000),
			str(self.f1 / 1000),
			str(self.us_duration / 1000),
			self.method,
			"-square" if self.square else ""
		)

	def _render(self, device):
		times = self.t_axis(device)
		t1 = times[-1]
		return chirp(
			t=times,
			f0=self.f0,
			f1=self.f1,
			t1=t1,
			method=self.method
		)

	def band(self, device=None):
		return (self.f0, self.f1)

class Noise(Pulse):
	def __init__(self, us_duration):
		super(Noise, self).__init__(us_duration)

	def __str__(self):
		return "noise-%sms" % (str(self.us_duration / 1000))

	def _render(self, device):
		return np.random.normal(0, 1, size=len(self.t_axis(device)))

	def band(self, device):
		# This bad boy is very broadband but we probably can get rid of audible
		# sound anyway, since the tweeters are loudest at > 15k.
		return (1.5e4, device.rate / 2)

class CombinedPulse(Pulse):
	def __init__(self, left, right):
		super(CombinedPulse, self).__init__(
			max(left.us_duration, right.us_duration),
			left.square and right.square
		)
		self.__rendered = None
		self.left_pulse = left
		self.right_pulse = right

	def render(self, device):
		assert device.channels == 2
		if not self.__rendered is None:
			return self.__rendered
		lr = self.left_pulse.render(device)
		rr = self.right_pulse.render(device)
		if len(lr) < len(rr):
			lr = zero_pad(lr, right_length=(len(rr) - len(lr)))
		if len(rr) < len(lr):
			rr = zero_pad(rr, right_length=(len(lr) - len(rr)))
		self.__rendered = np.stack((lr[:,0], rr[:,0]), axis=1)
		print self.__rendered.shape
		return self.__rendered

	def band(self):
		(l0, h0) = self.left_pulse.band()
		(l1, h1) = self.right_pulse.band()
		return (min(l0, l1), max(h0, h1))

	def __str__(self):
		return "combined-%s-%s" % (
			self.left_pulse, self.right_pulse
		)

