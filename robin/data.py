import numpy as np


def chunks(l, n):
    res = []
    for i in range(0, len(l), n):
        res.append(l[i : i + n])
    return res


def pad(array, length, pad):
    if len(array) == length:
        return array
    extra = [pad] * (length - len(array))
    return array + extra


def array_to_periods(array, device):
    return chunks(
        array.flatten().astype(device.np_format).tostring(), device.period_bytes()
    )


def periods_to_array(frames, device):
    channels = device.channels
    array = np.frombuffer(b''.join(frames), dtype=device.np_format)
    return np.reshape(array, (len(array) // channels, channels))