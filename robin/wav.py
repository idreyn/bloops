import os
import time
import io
import datetime as dt
import wavio
import base64

from .config import BASE_PATH


def now_stamp():
    t0 = time.time()
    return dt.datetime.fromtimestamp(t0).strftime("%Y-%m-%d-%H-%M-%S")


def save_wav_file(
    device, sound, name_append=None, prefix=(BASE_PATH + "/../recordings/"),
):
    rel_path = (
        prefix + dt.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d") + "/"
    )
    path = os.path.abspath(rel_path) + "/"
    if not os.path.exists(path):
        os.mkdir(path)
    filename = path + now_stamp() + "__" + (name_append if name_append else "") + ".wav"
    print(filename, sound.dtype)
    wavio.write(filename, sound, device.rate)
    return filename


def byte_encode_wav_data(device, sound):
    buffer = io.BytesIO()
    wavio.write(buffer, sound, device.rate)
    buffer.seek(0)
    return buffer.getvalue()
