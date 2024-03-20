import evdev
import threading

from robin.logger import log


class RemoteKeys:
    JOYSTICK_UP = "JOYSTICK_UP"
    JOYSTICK_DOWN = "JOYSTICK_DOWN"
    JOYSTICK_LEFT = "JOYSTICK_LEFT"
    JOYSTICK_RIGHT = "JOYSTICK_RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    MEDIA_NEXT = "MEDIA_NEXT"
    MEDIA_PREV = "MEDIA_PREV"
    MEDIA_PLAY = "MEDIA_PLAY"


KEYCODES = {
    RemoteKeys.JOYSTICK_UP: 208,
    RemoteKeys.JOYSTICK_DOWN: 168,
    RemoteKeys.JOYSTICK_LEFT: 165,
    RemoteKeys.JOYSTICK_RIGHT: 163,
    RemoteKeys.UP: 307,
    RemoteKeys.DOWN: 305,
    RemoteKeys.LEFT: 304,
    RemoteKeys.RIGHT: 308,
    RemoteKeys.MEDIA_PREV: 163,
    RemoteKeys.MEDIA_PLAY: 164,
    RemoteKeys.MEDIA_NEXT: 165,
}


def get_remote_device(name):
    while True:
        for fn in evdev.list_devices():
            dev = evdev.InputDevice(fn)
            if dev.name == name:
                return dev


def client(device_name, resolve_await, down=None, hold=None, up=None):
    while True:
        dev = get_remote_device(device_name)
        log(f"Bluetooth remote connected: {dev.name}")
        try:
            for event in dev.read_loop():
                kev = evdev.categorize(event)
                if isinstance(kev, evdev.KeyEvent):
                    if kev.keystate == kev.key_down:
                        resolve_await(kev.scancode)
                        if down and down.get(kev.scancode):
                            down.get(kev.scancode)()
                    if kev.keystate == kev.key_hold:
                        if hold and hold.get(kev.scancode):
                            hold.get(kev.scancode)()
                    if kev.keystate == kev.key_up:
                        if up and up.get(kev.scancode):
                            up.get(kev.scancode)()
        except (IOError, evdev.device.EvdevError) as e:
            log(e)
            log(f"Bluetooth remote disconnected: {dev.name}")


class BluetoothRemote(object):
    def __init__(self, name):
        self._up = {}
        self._down = {}
        self._hold = {}
        self._awaits = {}
        self._thread = threading.Thread(
            target=client,
            kwargs={
                "up": self._up,
                "down": self._down,
                "hold": self._hold,
                "device_name": name,
                "resolve_await": lambda k: self._resolve_await(k),
            },
            daemon=True,
        )
        self._thread.start()

    def register_handlers(self, down=None, hold=None, up=None):
        if down:
            for k in down:
                self._down[KEYCODES[k]] = down[k]
        if hold:
            for k in hold:
                self._hold[KEYCODES[k]] = hold[k]
        if up:
            for k in up:
                self._up[KEYCODES[k]] = up[k]

    def clear_key(self, key_name):
        keycode = KEYCODES[key_name]
        if self._awaits.get(keycode):
            self._awaits[keycode].clear()

    def await_key(self, key_name, and_clear=True, time=None):
        keycode = KEYCODES[key_name]
        if not self._awaits.get(keycode):
            self._awaits[keycode] = threading.Event()
        if and_clear:
            self._awaits[keycode].clear()
        return self._awaits[keycode].wait(time)

    def _resolve_await(self, keycode):
        if self._awaits.get(keycode):
            self._awaits[keycode].set()
