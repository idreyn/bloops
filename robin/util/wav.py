import io
import wavio
import scipy.io.wavfile as wavfile


def save_wav_file(filename, sound, rate):
    wavio.write(filename, sound, rate)


def byte_encode_wav_data(sound, rate):
    buffer = io.BytesIO()
    wavfile.write(buffer, rate, sound)
    buffer.seek(0)
    return buffer.getvalue()
