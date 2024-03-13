from .util import require_root

REQUIRED_LINES = [
    "dtoverlay=hifiberry-dacplusadcpro",
    "force_eeprom_read=0",
]

BOOT_CONFIG_PATH = "/boot/firmware/config.txt"


@require_root
def install_dtoverlay():
    print(f"Adding required lines to {BOOT_CONFIG_PATH}...")
    with open(BOOT_CONFIG_PATH, "r+") as file:
        existing_lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(existing_lines)
        for required_line in REQUIRED_LINES:
            if (
                required_line + "\n" not in existing_lines
                and required_line not in existing_lines
            ):
                file.write(f"{required_line}\n")


@require_root
def uninstall_dtoverlay():
    print(f"Removing required lines to {BOOT_CONFIG_PATH}...")
    with open(BOOT_CONFIG_PATH, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        for line in lines:
            if line.strip() not in REQUIRED_LINES:
                file.write(line)
