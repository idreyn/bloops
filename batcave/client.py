import logging
import time
import threading

from socketIO_client import SocketIO
from protocol import *

logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

def do_setup(batcave_host, get_device_info, callbacks):
	io = SocketIO(*BATCAVE_HOST)
	io.emit(Message.HANDSHAKE_DEVICE, DEVICE_INFO)
	for c in callbacks:
		io.on(c, callbacks.get(c))

def run_client(batcave_host, get_device_info, callbacks):
	t = threading.Thread(do_setup,
		args=(batcave_host, get_device_info, callbacks))
	t.start()

