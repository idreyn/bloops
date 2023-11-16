import socketio
import threading

from .protocol import Message

sio = None


def send_to_batcave_remote(*args, **kwargs):
    if sio and sio.connected:
        sio.emit(*args, **kwargs)


def client(batcave_host, get_device_status, get_device_info, callbacks):
    global sio
    sio = socketio.Client(reconnection=True)

    for event, handler in callbacks.items():
        sio.on(event, handler)

    @sio.event
    def connect():
        print("Connected to Batcave")
        handshake()

    @sio.event
    def disconnect():
        print("Disconnected from Batcave")

    def handshake():
        sio.emit(Message.HANDSHAKE_DEVICE, get_device_info())

    try:
        sio.connect(batcave_host)
    except:
        print("Could not connect to Batcave")

    try:
        while True:
            device_status = get_device_status()
            device_info = get_device_info()
            send_to_batcave_remote(
                Message.DEVICE_STATUS, {"status": device_status, "info": device_info}
            )
            sio.sleep(5)
    finally:
        sio.disconnect()


def run_batcave_client(*args):
    t = threading.Thread(target=client, args=args)
    t.daemon = True
    t.start()
