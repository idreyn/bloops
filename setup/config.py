from os import path
from shutil import copy2

from robin.constants import BASE_PATH

EXAMPLE_CONFIG = path.join(BASE_PATH, "config.example.json")
TARGET_CONFIG = path.join(BASE_PATH, "config.json")


def install_default_config():
    if not path.exists(TARGET_CONFIG):
        copy2(EXAMPLE_CONFIG, TARGET_CONFIG)
        print("Creating initial config.json...")
    else:
        print("Config exists, will not override.")
