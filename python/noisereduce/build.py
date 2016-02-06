from distutils.core import setup
from Cython.Build import cythonize

import numpy as np

setup(
	name="NoiseReduce",
	ext_modules=cythonize("noisereduce.pyx"),
	include_dirs=[np.get_include()]
)