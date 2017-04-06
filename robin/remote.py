import evdev
import threading

from config import BLUETOOTH_REMOTE_NAME

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
	RemoteKeys.LEFT: 114,
	RemoteKeys.RIGHT: 139,
}

def get_remote_device(name):
	while True:
		for fn in evdev.list_devices():
			dev = evdev.InputDevice(fn)
			if dev.name == name:
				return dev

def client(down=None, hold=None, up=None):
	down = {KEYCODES[k]: down[k] for k in down}
	hold = {KEYCODES[k]: hold[k] for k in hold}
	up = {KEYCODES[k]: up[k] for k in up}
	while True:
		dev = get_remote_device(BLUETOOTH_REMOTE_NAME)
		print "Bluetooth remote connected"
		try:
			for event in dev.read_loop():
				kev = evdev.categorize(event)
				if isinstance(kev, evdev.KeyEvent):
					if kev.keystate == kev.key_down:
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
			
def connect_to_remote(*args, **kwargs):
	t = threading.Thread(target=client, args=args, kwargs=kwargs)
	t.daemon = False
	t.start()

if __name__ == "__main__":
	client(False)