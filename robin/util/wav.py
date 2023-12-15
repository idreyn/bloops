import io
import wavio


def save_wav_file(filename, sound, rate):
    wavio.write(filename, sound, rate)


def byte_encode_wav_data(sound, rate):
    buffer = io.BytesIO()
    wavio.write(buffer, sound, rate)
    buffer.seek(0)
    return buffer.getvalue()
