from audio import *
from config import *
from gpio import *
from process import *
from pulse import *
from save import *

dac = AudioDevice('dac', 192000)
ultramics = AudioDevice('ultramics', 192000)

audio = Audio(ultramics, dac)

def simple_loop(pulse_source):
	pulse = pulse_source(dac)
	print "do thing", str(pulse)
	with audio as (record, emit, playback):
		with emitters:
			emit.write_array(Silence(dac, 1e4).render())
			emit.write_array(pulse_source(dac).render())
			rec = record.read_array(0.1)
	print rec.shape
	save_file(ultramics, rec)
