import numpy as np

def chunks(l, n):
	res = []
	for i in xrange(0, len(l), n):
		res.append(l[i:i+n])
	return res

def array_to_periods(array, device):
    return chunks(
        np.transpose(arr)
        .flatten()
        .astype(device.np_format)
        .tostring(),
        device.period_bytes()
    )

def periods_to_array(frames, device):
	channels = device.channels
	array = np.fromstring(
		''.join(frames),
		dtype=device.np_format
	)
	return np.transpose(
		np.reshape(
			array,
			(len(array) / channels, channels)
		)
	)