#! /usr/bin/python

from __future__ import division

import time
import datetime
import sys

from audio import Audio
from config import (ULTRAMICS, DAC, IP, DEVICE_ID, has_required_devices,
                    print_device_availability)
from config_secret import BATCAVE_HOST
from echolocate import simple_loop, Echolocation
from gpio import (emitter_enable, emitter_battery_low, device_battery_low,
                  power_led)
from profile import *
from pulse import *
from remote import *

import batcave.client as batcave
from batcave.protocol import Message, DeviceStatus
from batcave.debug_override import DebugOverride

import process.pipeline as pipeline

audio = Audio(ULTRAMICS, DAC)
profile = None
busy = False
connected_remotes = 0

def handle_override(overrides):
    emitter_enable.set(overrides.force_enable_emitters)
    profile.playback = not overrides.disable_playback
    profile.set_save_all(not overrides.disable_save)
    profile.set_save_prefix(overrides.save_prefix)

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
    profile.current_pulse = pulse_from_dict(pulse_dict)


def on_set_ms_record_duration(d):
    profile.us_record_duration = d * 1000


def on_trigger_pulse(pulse=None):
    global busy
    if busy:
        return
    pulse = pulse or profile.current_pulse
    print "Emitting", pulse
    busy = True
    try:
        simple_loop(
            Echolocation(
                pulse,
                profile.slowdown,
                audio.record_device,
                profile.us_record_duration,
                profile.us_silence_before
            ),
            audio,
            profile,
            pipeline.STANDARD_PIPELINE,
        )
    finally:
        busy = False


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

def make_pulse_callback(pulse):
    def inner():
        on_trigger_pulse(pulse)
    return inner

def main():
    global profile
    if len(sys.argv) > 1:
        prof_path = sys.argv[1]
        print "Using profile from %s" % prof_path
        profile = Profile.from_file(prof_path)
    else:
        profile = Profile()
        print "Using default profile"
    if not has_required_devices():
        print_device_availability()
        print "Missing audio hardware. exiting."
        os._exit(0)
    audio.start()
    print "Starting batcave client..."
    batcave.run_client(
        BATCAVE_HOST,
        get_device_status,
        get_device_info,
        {
           Message.CONNECT: on_connected,
           Message.RECONNECT: on_connected,
           Message.DISCONNECT: on_disconnect,
           Message.TRIGGER_PULSE: on_trigger_pulse,
           Message.UPDATE_PULSE: on_update_pulse,
           Message.SET_RECORD_DURATION: on_set_ms_record_duration,
           Message.UPDATE_OVERRIDES: on_update_overrides,
           Message.DEVICE_REMOTE_CONNECT: on_remote_connect,
           Message.DEVICE_REMOTE_DISCONNECT: on_remote_disconnect,
        }
    )
    print "Initializing connection to Bluetooth remote..."
    connect_to_remote(
        down={
            k: make_pulse_callback(profile.remote_mapping[k])
            for k in profile.remote_mapping
        },
        hold={
            RemoteKeys.JS_UP: lambda:
                emitter_enable.set(True)
        },
        up={
            RemoteKeys.JS_UP: lambda:
                (not busy) and emitter_enable.set(False)
        }
    )
    for i in xrange(3):
        emitter_enable.set(True)
        time.sleep(0.1)
        emitter_enable.set(False)
        time.sleep(0.1)

try:
    main()
    while True:
        time.sleep(0.01)
except KeyboardInterrupt:
    import os
    os._exit(0)
