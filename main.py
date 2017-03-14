from __future__ import division

import time
import datetime

import alsaaudio as aa
import numpy as np

from config import *
from echolocate import *
from gpio import *
from pulse import *

from util import app_running, kill_app
from batcave.client import run_client, emit
from batcave.protocol import *
from batcave.debug_override import *

last_pulse_dict = None
connected_remotes = 0
pulse_source = default_pulse_source()

def handle_override(o):
	emitters.set(o.force_enable_emitters)

def on_connected():
	print "we're connected!"

def on_disconnect():
	print "we're disconnected."

def on_remote_connect():
	global connected_remotes
	connected_remotes += 1

def on_remote_disconnect():
	global connected_remotes
	connected_remotes -= 1
	if connected_remotes == 0:
		handle_override(DebugOverride())

def on_update_overrides(o):
	handle_override(DebugOverride.from_dict(o))

def on_update_pulse(p):
	global pulse_source, last_pulse_dict
	if p != last_pulse_dict:
		last_pulse_dict = p
		pulse_source = pulse_source_from_dict(p)

def on_trigger_pulse():
	global pulse_source
	simple_loop(pulse_source)
	
def get_device_status():
	return DeviceStatus.READY

def get_device_info():
	return {
		'id': DEVICE_ID,
		'ip': IP,
		'deviceVoltageLow': power_led.read(),
		'deviceBatteryLow': device_battery_low.read(),
		'emitterBatteryLow': emitter_battery_low.read(),
		'bluetoothConnections': "Unknown",
		'lastSeen': str(datetime.datetime.now()),
		'pulse': last_pulse_dict,
	}

def main():
	run_client(BATCAVE_HOST, 
		get_device_status, 
		get_device_info,
		{
			Message.CONNECT: on_connected,
			Message.RECONNECT: on_connected,
			Message.DISCONNECT: on_disconnect,
			Message.TRIGGER_PULSE: on_trigger_pulse,
			Message.UPDATE_PULSE: on_update_pulse,
			Message.UPDATE_OVERRIDES: on_update_overrides,
			Message.DEVICE_REMOTE_CONNECT: on_remote_connect,
			Message.DEVICE_REMOTE_DISCONNECT: on_remote_disconnect,
		},
		app_running
	)

try:
	# main()
	while True:
		time.sleep(1)
                simple_loop(pulse_source)
except KeyboardInterrupt:
	kill_app()
