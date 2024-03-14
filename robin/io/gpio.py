import time
import gpiod
from gpiod.line import Direction, Value

CHIP_NAME = "/dev/gpiochip4"


class GPIOWrite(object):
    def __init__(self, pin, ms_wait=0):
        self.pin = pin
        self.ms_wait = ms_wait
        self.chip = gpiod.Chip(CHIP_NAME)
        self.request = self.chip.request_lines(
            config={self.pin: gpiod.LineSettings(direction=Direction.OUTPUT)}
        )

    def set(self, on):
        self.request.set_value(self.pin, Value.ACTIVE if on else Value.INACTIVE)

    def __enter__(self):
        self.set(True)
        time.sleep(self.ms_wait / 1000.0)

    def __exit__(self):
        self.set(False)


class GPIORead(object):
    def __init__(self, pin):
        self.pin = pin
        self.chip = gpiod.Chip(CHIP_NAME)
        self.request = self.chip.request_lines(
            config={self.pin: gpiod.LineSettings(direction=Direction.INPUT)}
        )

    def read(self) -> bool:
        return self.request.get_value(self.pin) == Value.ACTIVE


emitter_enable = GPIOWrite(16, ms_wait=1)
emitter_battery_low = GPIORead(12)
device_battery_low = GPIORead(25)
