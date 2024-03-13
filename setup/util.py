import os  # noqa: F401
import functools
import elevate


def require_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        elevate.elevate(show_console=True)
        return func(*args, **kwargs)

    return wrapper
