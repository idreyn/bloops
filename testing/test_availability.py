import test

from audio import AudioDevice, Audio

a = Audio(
    record_device=AudioDevice("ultramics", 200000),
    emit_device=AudioDevice("dac", 192000),
)

try:
    while True:
        print("awaiting available")
        a.await_available()
        print("awaiting unavailable")
        a.await_unavailable()
except KeyboardInterrupt:
    pass
