class DeviceStatus:
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"
    BUSY = "busy"
    HARDWARE_UNAVAILABLE = "hardware-unavailable"
    READY = "ready"


class RemoteStatus:
    NO_SOCKET = "no-socket"
    DISCONNECTED = "disconnected"


class Message:
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    RECONNECT = "reconnect"
    HANDSHAKE_REMOTE = "handshake-remote"
    HANDSHAKE_DEVICE = "handshake-device"
    DEVICE_LISTING = "device-listing"
    CHOOSE_DEVICE = "choose-device"
    DEVICE_CHOICE_INVALID = "device-choice-invalid"
    DEVICE_CHOICE_SUCCESSFUL = "device-choice-successful"
    DEVICE_STATUS = "device-status"
    DEVICE_REMOTE_CONNECT = "device-remote-connect"
    DEVICE_REMOTE_DISCONNECT = "device-remote-disconnect"
    UPDATE_CONFIG = "update-config"
    TRIGGER_PULSE = "trigger-pulse"
    UPDATE_OVERRIDES = "update-overrides"
    RESTART_DEVICE = "restart-device"
    AUDIO = "audio"
