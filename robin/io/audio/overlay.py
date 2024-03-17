from .devices import BATHAT, HIFIBERRY
from robin.logger import log

HAT_OVERLAY_NAMES = {
    "cs4270": BATHAT,
    "hifiberry-dacplusadcpro": HIFIBERRY,
}

BOOT_CONFIG = "/boot/firmware/config.txt"

DTOVERLAY_KEY = "dtoverlay"


def print_possible_overlays():
    for overlay_name in HAT_OVERLAY_NAMES.keys():
        log(f"{DTOVERLAY_KEY}={overlay_name}")


def get_configured_hat_device():
    with open(BOOT_CONFIG, "r") as config:
        for line in config.readlines():
            if line.startswith(DTOVERLAY_KEY):
                _, overlay_name = line.split("=")
                overlay_name = overlay_name.strip()
                hat = HAT_OVERLAY_NAMES.get(overlay_name)
                if not hat:
                    log(f"No device available for {DTOVERLAY_KEY}={overlay_name}")
                return hat
    log(f"No {DTOVERLAY_KEY} entry found. Add one of these to {BOOT_CONFIG}:")
    print_possible_overlays()
    return None
