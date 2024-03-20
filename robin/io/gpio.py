import time
import RPi.GPIO as gpio

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)


class GPIOWrite(object):
    def __init__(self, pin, ms_wait=0):
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


class GPIORead(object):
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(self.pin, gpio.IN)

    def read(self):
        return gpio.input(self.pin)

    def on(self, callback):
        def handler():
            callback(self.read())

        self._handler = handler
        gpio.add_event_detect(self.pin, gpio.RISING)
        gpio.add_event_detect(self.pin, gpio.FALLING)
        gpio.add_event_callback(self.pin, handler)


emitter_enable = GPIOWrite(16, ms_wait=1)
emitter_battery_okay = GPIORead(6)
device_battery_okay = GPIORead(5)
