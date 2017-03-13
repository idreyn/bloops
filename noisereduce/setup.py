from os import path
from distutils.core import setup
from Cython.Build import cythonize

import numpy as np

# Run me from the root of the repository!

setup(
	name="NoiseReduce",
	ext_modules=cythonize("robin/noisereduce/noisereduce.pyx"),
	include_dirs=[np.get_include()]
)