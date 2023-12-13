import numpy as np
import alsaaudio as aa


def format_size(fmt):
    return {
        aa.PCM_FORMAT_S16_LE: 2,
        aa.PCM_FORMAT_S24_LE: 3,
        aa.PCM_FORMAT_FLOAT_LE: 4,
    }.get(fmt)


def format_np(fmt):
    return {aa.PCM_FORMAT_S16_LE: np.int16, aa.PCM_FORMAT_FLOAT_LE: np.float32}.get(fmt)
