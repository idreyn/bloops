import subprocess
from os import path
import sys

ROOT = path.join(path.dirname(__file__), "..")


def install_cython():
    # TODO(ian): We should do literally anything else here
    print("Compiling Cython code...")
    subprocess.call(
        args=[sys.executable, "robin/noisereduce/setup.py", "build_ext", "--inplace"],
        cwd=ROOT,
    )
