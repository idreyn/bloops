import alsaaudio as aa
from config import *
from stream import *

print aa.pcms()

d = Device('ultramics', 192000)
s = Stream(d, True)
print s.read_array(2).shape