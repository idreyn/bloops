import evdev
import threading

from config import BLUETOOTH_REMOTE_NAME

class RemoteKeys:
	JS_UP = 208
	JS_DOWN = 168
	JS_LEFT = 165
	JS_RIGHT = 163
	UP = 115
	DOWN = 113
	LEFT = 114
	RIGHT = 139

def get_remote_device(name):
	while True:
		for fn in evdev.list_devices():
			dev = evdev.InputDevice(fn)
			if dev.name == name:
				return dev

def client(down=None, hold=None, up=None):
	while True:
		dev = get_remote_device(BLUETOOTH_REMOTE_NAME)
		print "bluetooth remote connected!"
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
		except (IOError, evdev.device.EvdevError):
			print "bluetooth remote appears to be disconnected"
			
def connect_to_remote(*args, **kwargs):
	t = threading.Thread(target=client, args=args, kwargs=kwargs)
	t.daemon = False
	t.start()

if __name__ == "__main__":
	client(False)