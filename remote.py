import evdev
import threading

class RemoteKeys:
	JS_UP = "JS_UP"
	JS_DOWN = "JS_DOWN"
	JS_LEFT = "JS_LEFT"
	JS_RIGHT = "JS_RIGHT"
	UP = "UP"
	DOWN = "DOWN"
	LEFT = "LEFT"
	RIGHT = "RIGHT"

KEYCODES = {
	RemoteKeys.JS_UP: 208,
	RemoteKeys.JS_DOWN: 168,
	RemoteKeys.JS_LEFT: 165,
	RemoteKeys.JS_RIGHT: 163,
	RemoteKeys.UP: 115,
	RemoteKeys.DOWN: 113,
	RemoteKeys.LEFT: 28,
	RemoteKeys.RIGHT: 158,
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
		print "Bluetooth remote connected"
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
			print e
			print "Bluetooth remote disconnected"


class Remote(object):
    def __init__(self, name):
        self._up = {}
        self._down = {}
        self._hold = {}
        self._awaits = {}
        self._thread = threading.Thread(
            target=client,
            kwargs={
                'up': self._up,
                'down': self._down,
                'hold': self._hold,
                'device_name': name,
                'resolve_await': lambda k: self._resolve_await(k)
            }
        )
        self._thread.daemon = False
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

