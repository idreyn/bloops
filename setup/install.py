from .dtoverlay import install_dtoverlay, uninstall_dtoverlay
from .systemd import install_systemd_service, uninstall_systemd_service
from .githooks import install_githooks, uninstall_githooks


def install_to_rpi():
    install_dtoverlay()
    install_systemd_service()
    install_githooks()


def uninstall_from_rpi():
    uninstall_dtoverlay()
    uninstall_systemd_service()
    uninstall_githooks()
