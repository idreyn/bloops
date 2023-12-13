import os
import time
import datetime
import click
from threading import Event

from .io.audio import Audio
from .io.remote import BluetoothRemote
from .constants import ROBIN
from .devices import BATHAT, HEADPHONES
from .echolocation import (
    echolocate,
    Echolocation,
    pulse_from_dict,
    dict_from_pulse,
)
from .io.gpio import emitter_enable, emitter_battery_low, device_battery_low
from .profile import *
from .repl import run_repl
from .pipeline import STANDARD_PIPELINE
from .util.net import get_ip_address

from .batcave.client import run_batcave_client
from .batcave.server import run_batcave_server
from .batcave.protocol import Message, DeviceStatus
from .batcave.debug_override import DebugOverride


# ron paul dot gif
print(ROBIN)

audio = Audio(record_device=BATHAT, emit_device=BATHAT, playback_device=HEADPHONES)
profile = None
busy = False
connected_remotes = 0


def handle_override(overrides):
    emitter_enable.set(overrides.force_enable_emitters)
    profile.playback = not overrides.disable_playback
    profile.set_save_all(not overrides.disable_save)
    profile.set_save_prefix(overrides.save_prefix)


def on_connected():
    print("Batcave client connected")


def on_disconnect():
    print("Batcave client disconnected")


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
    print("Assigning", pulse, "to", button)
    profile.remote_mapping[button] = pulse


def on_update_label(label):
    profile.set_save_prefix(label)


def on_trigger_pulse(pulse=None):
    global busy
    if busy:
        return
    pulse = pulse or profile.current_pulse
    print("Emitting", pulse)
    busy = True
    try:
        echolocate(
            Echolocation(
                pulse,
                profile.slowdown,
                audio.record_device,
                profile.us_record_duration,
                profile.us_silence_before,
            ),
            audio,
            profile,
            STANDARD_PIPELINE,
        )
    finally:
        busy = False


def get_device_status():
    return DeviceStatus.READY


def get_device_info():
    global profile
    return {
        "id": profile.device_id,
        "ip": get_ip_address(),
        "deviceBatteryLow": device_battery_low.read(),
        "emitterBatteryLow": emitter_battery_low.read(),
        "bluetoothConnections": str(connected_remotes),
        "lastSeen": str(datetime.datetime.now()),
        "pulse": dict_from_pulse(profile.current_pulse),
    }


def make_pulse_callback(button):
    def inner():
        on_trigger_pulse(profile.remote_mapping[button])

    return inner


batcave_handlers = {
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


@click.command()
@click.option("--reverse-channels/--no-reverse-channels", default=False, required=False)
@click.option("--loopback-test/--no-loopback-test", default=False, required=False)
@click.argument("profile_path", type=click.Path(exists=True), required=False)
def main(reverse_channels, loopback_test, profile_path):
    global profile
    if not audio.devices_available():
        print(audio.device_availability())
        print("Missing audio hardware, exiting.")
        os._exit(0)
    if profile_path:
        print("Using profile from %s" % profile_path)
        profile = Profile.from_file(profile_path)
    else:
        profile = Profile()
        print("Using default profile")
    if reverse_channels != None:
        profile.reverse_channels = reverse_channels
        print("Override reverse_channels to %s" % reverse_channels)
    if len(profile.remote_mapping) == 0:
        print("Warning: profile has no remote key mappings")
    print("Starting audio I/O...")
    audio.start()
    exit_event = Event()
    if profile.batcave_self_host:
        print("Running Batcave server locally...")
        run_batcave_server(exit_event)
    run_batcave_client(
        profile,
        get_device_status,
        get_device_info,
        batcave_handlers,
    )
    print("Waiting for Bluetooth remote...")
    remote = BluetoothRemote(profile.remote_name)
    if loopback_test:
        remote.clear_key(RemoteKeys.RIGHT)
        print("Ready earbuds and press RIGHT on the remote")
        print("Waiting for key...")
        while not remote.await_key(RemoteKeys.RIGHT, time=0, and_clear=False):
            audio.loopback()
    remote.register_handlers(
        down={k: make_pulse_callback(k) for k in profile.remote_mapping},
        hold={RemoteKeys.JS_UP: lambda: emitter_enable.set(True)},
        up={RemoteKeys.JS_UP: lambda: (not busy) and emitter_enable.set(False)},
    )
    for _ in range(3):
        emitter_enable.set(True)
        time.sleep(0.05)
        emitter_enable.set(False)
        time.sleep(0.05)
    print("Ready to echolocate!")
    run_repl(on_trigger_pulse, profile, exit_event)
    exit_event.wait()


main()
