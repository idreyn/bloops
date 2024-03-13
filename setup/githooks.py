import shutil
from os import path, remove, listdir, makedirs, chmod, stat

CURRENT_DIR = path.dirname(path.abspath(__file__))
SOURCE_DIR = path.join(CURRENT_DIR, "githooks")
TARGET_DIR = path.abspath(path.join(CURRENT_DIR, "..", ".git", "hooks"))


def install_githooks():
    print("Installing githooks...")
    if not path.exists(TARGET_DIR):
        makedirs(TARGET_DIR)
    for filename in listdir(SOURCE_DIR):
        target_path = path.join(TARGET_DIR, filename)
        shutil.copy2(path.join(SOURCE_DIR, filename), target_path)
        chmod(target_path, stat(target_path).st_mode | 0o111)


def uninstall_githooks():
    print("Uninstalling githooks...")
    for filename in listdir(SOURCE_DIR):
        target_file_path = path.join(TARGET_DIR, filename)
        if path.exists(target_file_path):
            remove(target_file_path)
