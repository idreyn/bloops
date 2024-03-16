from os import path
import subprocess
import threading
from psutil import Process

from robin.constants import BASE_PATH

BATCAVE_DIR = path.join(BASE_PATH, "batcave_server")


def build_batcave_server(config):
    if not path.exists(path.join(BATCAVE_DIR, "node_modules")):
        subprocess.run(
            args=["npm", "install"],
            cwd=BATCAVE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if config.current.batcave.build_dev:
        print("Watching for changes to Batcave frontend...")
        subprocess.Popen(
            args=["npm", "run", "dev"],
            cwd=BATCAVE_DIR,
        )
    if not path.exists(path.join(BATCAVE_DIR, "dist")):
        subprocess.run(
            args=["npm", "run", "build"],
            cwd=BATCAVE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _run_batcave_server(exit_event, config):
    build_batcave_server(config)
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


def run_batcave_server(config, exit_event):
    server_thread = threading.Thread(
        target=_run_batcave_server,
        args=[exit_event, config],
        daemon=False,
    )
    server_thread.start()
