from __future__ import division

import time
import datetime

from audio import Audio
from config import ULTRAMICS, DAC, IP, DEVICE_ID
from config_secret import BATCAVE_HOST
from echolocate import simple_loop
from gpio import (emitter_enable, emitter_battery_low, device_battery_low,
                        power_led)
from pulse import default_pulse, pulse_from_dict

from util import app_running, kill_app
from batcave.client import run_client
from batcave.protocol import Message, DeviceStatus
from batcave.debug_override import DebugOverride

AUDIO = Audio(ULTRAMICS, DAC)

ms_record_duration = 100
connected_remotes = 0
last_pulse_dict = None
pulse = default_pulse()


def handle_override(overrides):
    emitter_enable.set(overrides.force_enable_emitters)


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


def on_update_overrides(overrides):
    handle_override(DebugOverride.from_dict(overrides))


def on_update_pulse(pulse_dict):
    global pulse, last_pulse_dict
    if pulse != last_pulse_dict:
        last_pulse_dict = pulse_dict
        pulse = pulse_from_dict(pulse_dict)

def on_set_record_duration(d):
	global ms_record_duration
	ms_record_duration = d

def on_trigger_pulse():
    simple_loop(Echolocation(pulse, 20, 1000 * ms_record_duration), AUDIO)


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
    print "running client from main..."
    run_client(BATCAVE_HOST,
               get_device_status,
               get_device_info,
               {
                   Message.CONNECT: on_connected,
                   Message.RECONNECT: on_connected,
                   Message.DISCONNECT: on_disconnect,
                   Message.TRIGGER_PULSE: on_trigger_pulse,
                   Message.UPDATE_PULSE: on_update_pulse,
                   Message.SET_RECORD_DURATION: on_set_record_duration,
                   Message.UPDATE_OVERRIDES: on_update_overrides,
                   Message.DEVICE_REMOTE_CONNECT: on_remote_connect,
                   Message.DEVICE_REMOTE_DISCONNECT: on_remote_disconnect,
               },
               app_running)

try:
    main()
    while True:
        time.sleep(0.01)
except KeyboardInterrupt:
    kill_app()
