import sys

def round_to_nearest(x,clip):
	return x * round(float(x) / clip)

def de_interleave(arr):
	a = []
	b = []
	for i, x in enumerate(arr):
		if i % 2 == 0:
			a.append(x)
		else:
			b.append(x)
	return a,b

def log(str,level=0):
	print str

def log_fail(str,level=0):
	log(str,level)
	sys.exit(0)