import alsaaudio as aa
from config import *
from stream import *

print aa.pcms()

d = Device('ultramics', 200000)
s = Stream(d, True)
