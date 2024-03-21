import logging

_logger = logging.getLogger("robin")
_logger.setLevel(logging.INFO)


def log(message: object, level: int = logging.INFO):
    from robin.batcave.client import send_to_batcave_remote
    from robin.batcave.protocol import Message

    print(message)
    _logger.log(level, message)
    send_to_batcave_remote(Message.DEVICE_LOG, str(message))
