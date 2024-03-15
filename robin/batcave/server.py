from os import path
import subprocess
import threading
from psutil import Process

from robin.constants import BASE_PATH

BATCAVE_DIR = path.join(BASE_PATH, "batcave_server")


def build_batcave_server():
    if not path.exists(path.join(BATCAVE_DIR, "node_modules")):
        subprocess.run(
            args=["npm", "install"],
            cwd=BATCAVE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if not path.exists(path.join(BATCAVE_DIR, "dist")):
        subprocess.run(
            args=["npm", "run", "build"],
            cwd=BATCAVE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _run_batcave_server(exit_event):
    build_batcave_server()
    server = subprocess.Popen(
        args=["npm", "run", "start"],
        cwd=BATCAVE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    exit_event.wait()
    for child in Process(pid=server.pid).children(recursive=True):
        child.terminate()
    server.terminate()


def run_batcave_server(exit_event):
    server_thread = threading.Thread(
        target=_run_batcave_server,
        args=[exit_event],
        daemon=False,
    )
    server_thread.start()
