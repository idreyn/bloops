import shutil  # noqa: F401
from os import path, remove

from .util import require_root

REPO_PATH = path.abspath(path.join(path.dirname(__file__), ".."))

SERVICE_TEXT = f"""
[Unit]
Description=Start Robin

[Service]
Type=simple
ExecStart={REPO_PATH}/start.sh > {REPO_PATH}/robin.log 2>&1
User=robin
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

DEST_PATH = "/etc/systemd/system/robin.service"


@require_root
def install_systemd_service():
    print("Installing systemd service...")
    with open(DEST_PATH, "w") as file:
        file.write(SERVICE_TEXT)


@require_root
def uninstall_systemd_service():
    print("Uninstalling systemd service...")
    if path.exists(DEST_PATH):
        remove(DEST_PATH)
