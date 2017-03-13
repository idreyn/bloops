from __future__ import division

import time
import RPi.GPIO as gpio

from stream import *
from record import *

gpio.setmode(gpio.BCM)


class GPIOHold(object):
	def __init__(self, pin, ms_wait=200):
		self.pin = pin
		self.ms_wait = ms_wait
		gpio.setup(self.pin, gpio.OUT)

	def set(self, on):
		gpio.output(self.pin, gpio.HIGH if on else gpio.LOW)

	def __enter__(self, *rest):
		gpio.output(self.pin, gpio.HIGH)
		time.sleep(self.ms_wait / 1000)

	def __exit__(self, *rest):
		self.set(False)

emitters = GPIOHold(17)