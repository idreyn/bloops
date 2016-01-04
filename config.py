import pyaudio

FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 192000
CHUNK = 1024

SERIAL_PORT = '/dev/tty.usbmodem1412'
SERIAL_BAUD = 9600