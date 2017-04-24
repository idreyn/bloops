#! /usr/bin/python

from __future__ import division

import os
import time
import datetime
import sys
import base64


from audio import Audio
from config import (ULTRAMICS, DAC, IP, DEVICE_ID, has_required_devices,
                    print_device_availability)

from config_secret import BATCAVE_HOST
from data import array_to_periods

from echolocate import simple_loop, Echolocation

from gpio import emitter_enable

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
    print "Batcave client connected"


def on_disconnect():
    print "Batcave client disconnected"


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


def on_set_record_duration(d):
    profile.us_record_duration = d

def on_assign_pulse(info):
    button = info["button"]
    pulse = pulse_from_dict(info["pulse"])
    print "Assigning", pulse, "to", button
    profile.remote_mapping[button] = pulse

def on_update_label(label):
    profile.set_save_prefix(label)

def on_trigger_pulse(pulse=None):
    global busy
    if busy:
        return
    pulse = pulse or profile.current_pulse
    print "Emitting", pulse
    busy = True
    try:
        ex = simple_loop(
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
        """
        if ex.recording_filename:
            encoded = base64.b64encode(open(ex.recording_filename, 'r').read())
            batcave.emit(Message.AUDIO, {
                'pulse': dict_from_pulse(pulse),
                'audio': encoded
            })
            print "Sent audio to Batcave"
        else:
            print "No audio to send"
        """
    finally:
        busy = False


def get_device_status():
    return DeviceStatus.READY

def get_device_info():
    return {
        'id': DEVICE_ID,
        'ip': IP,
        'deviceVoltageLow': False, # power_led.read(),
        'deviceBatteryLow': False, # device_battery_low.read(),
        'emitterBatteryLow': False, # emitter_battery_low.read(),
        'bluetoothConnections': "Unknown",
        'lastSeen': str(datetime.datetime.now()),
        'pulse': dict_from_pulse(profile.current_pulse),
    }

def make_pulse_callback(button):
    def inner():
        on_trigger_pulse(profile.remote_mapping[button])
    return inner

def main():
    global profile
    reverse = False
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        print "Reversing channels"
        reverse = True
        sys.argv.pop(0) # So jank, please fix
    if len(sys.argv) > 1:
        prof_path = sys.argv[1]
        print "Using profile from %s" % prof_path
        profile = Profile.from_file(prof_path)
    else:
        profile = Profile()
        print "Using default profile"
    if reverse:
        profile.reverse_channels = True
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
           Message.SET_RECORD_DURATION: on_set_record_duration,
           Message.UPDATE_OVERRIDES: on_update_overrides,
           Message.DEVICE_REMOTE_CONNECT: on_remote_connect,
           Message.DEVICE_REMOTE_DISCONNECT: on_remote_disconnect,
           Message.ASSIGN_PULSE: on_assign_pulse,
           Message.UPDATE_LABEL: on_update_label,
        }
    )
    print "Initializing connection to Bluetooth remote..."
    connect_to_remote(
        down={
            k: make_pulse_callback(k)
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
    os._exit(0)
