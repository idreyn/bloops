import os
import time
import datetime
import click
from threading import Event

from .io.audio import Audio
from .io.remote import BluetoothRemote
from .constants import ROBIN, BASE_PATH
from .io.audio.devices import BATHAT, HEADPHONES, HIFIBERRY, NULL, pick_available_device
from .echolocation.echolocate import echolocate

from .io.ad5252 import AD5252
from .io.camera import Camera
from .io.gpio import emitter_enable, emitter_battery_okay, device_battery_okay
from .io.remote import RemoteKeys
from .repl import run_repl
from .pipeline import STANDARD_PIPELINE
from .util.net import get_ip_address, get_hostname
from .config import Config
from .logger import log

from .batcave.client import run_batcave_client
from .batcave.server import run_batcave_server
from .batcave.protocol import Message, DeviceStatus
from .batcave.debug_override import DebugOverride


# ron paul dot gif
log(ROBIN)

codec_device = pick_available_device([BATHAT, HIFIBERRY], as_input=True)
playback_device = pick_available_device([HEADPHONES, NULL], as_input=False)

if playback_device is NULL:
    log("Warning: No headphones detected.")

audio = Audio(
    record_device=codec_device,
    emit_device=codec_device,
    playback_device=playback_device,
)

camera = None
config: Config = None
busy = False
batcave_connections = 0
bluetooth_remote: BluetoothRemote = None


def handle_override(overrides):
    emitter_enable.set(overrides.force_enable_emitters)


def on_connected():
    log("Batcave client connected")


def on_disconnect():
    log("Batcave client disconnected")


def on_remote_connect():
    global batcave_connections
    batcave_connections += 1


def on_remote_disconnect():
    global batcave_connections
    batcave_connections -= 1
    if batcave_connections == 0:
        handle_override(DebugOverride())


def on_update_overrides(overrides):
    handle_override(DebugOverride.from_dict(overrides))


def on_trigger_pulse(pulse=None):
    global busy, config
    if busy:
        return
    pulse = pulse or config.current.pulse
    log(f"Emitting {pulse}")
    busy = True
    try:
        echolocate(
            pulse,
            audio,
            camera,
            config,
            STANDARD_PIPELINE,
        )
    finally:
        busy = False


def on_update_config(update):
    config.update_config_json(update["config"], update["save"])


def get_device_status():
    return DeviceStatus.READY


def get_device_info():
    bluetooth_name = (
        bluetooth_remote.name
        if bluetooth_remote and bluetooth_remote.connected
        else "None"
    )
    return {
        "id": get_hostname(),
        "ip": get_ip_address(),
        "deviceBatteryLow": not device_battery_okay.read(),
        "emitterBatteryLow": not emitter_battery_okay.read(),
        "batcaveConnections": str(batcave_connections),
        "bluetoothRemote": bluetooth_name,
        "lastSeen": str(datetime.datetime.now()),
    }


def make_pulse_callback(button):
    pulse = config.current.remote.remote_keys[button]

    def inner():
        on_trigger_pulse(config.current.pulse if pulse == "current" else pulse)

    return inner


batcave_handlers = {
    Message.CONNECT: on_connected,
    Message.RECONNECT: on_connected,
    Message.DISCONNECT: on_disconnect,
    Message.TRIGGER_PULSE: on_trigger_pulse,
    Message.UPDATE_OVERRIDES: on_update_overrides,
    Message.DEVICE_REMOTE_CONNECT: on_remote_connect,
    Message.DEVICE_REMOTE_DISCONNECT: on_remote_disconnect,
    Message.UPDATE_CONFIG: on_update_config,
}


@click.command()
@click.option("--loopback-test/--no-loopback-test", default=False, required=False)
@click.argument(
    "config_path",
    type=click.Path(exists=True),
    default=f"{BASE_PATH}/config.json",
    required=False,
)
def main(loopback_test, config_path):
    global camera, config, bluetooth_remote
    config = Config(config_path)
    if not audio.devices_available():
        log(audio.device_availability())
        log("Missing audio hardware, exiting.")
        os._exit(0)
    if (
        config.current.remote.remote_name
        and len(config.current.remote.remote_keys) == 0
    ):
        log("Warning: remote name specified but config has no remote key mappings")
    if audio.record_device == BATHAT:
        ad = AD5252()
        ad.write_all(10)
    log("Starting audio I/O...")
    audio.start()
    exit_event = Event()
    camera = Camera()
    if config.current.batcave.self_host:
        log("Running Batcave server locally...")
        run_batcave_server(config, exit_event)
    run_batcave_client(
        config,
        get_device_status,
        get_device_info,
        batcave_handlers,
    )
    log("Waiting for Bluetooth remote...")
    bluetooth_remote = BluetoothRemote(config.current.remote.remote_name)
    if loopback_test:
        bluetooth_remote.clear_key(RemoteKeys.RIGHT)
        log("Ready earbuds and press RIGHT on the remote")
        log("Waiting for key...")
        while not bluetooth_remote.await_key(RemoteKeys.RIGHT, time=0, and_clear=False):
            audio.loopback()
    bluetooth_remote.register_handlers(
        down={k: make_pulse_callback(k) for k in config.current.remote.remote_keys},
        hold={RemoteKeys.JOYSTICK_UP: lambda: emitter_enable.set(True)},
        up={RemoteKeys.JOYSTICK_UP: lambda: (not busy) and emitter_enable.set(False)},
    )
    for _ in range(3):
        emitter_enable.set(True)
        time.sleep(0.05)
        emitter_enable.set(False)
        time.sleep(0.05)
    log("Ready to echolocate!")
    run_repl(on_trigger_pulse, config, exit_event)
    exit_event.wait()
