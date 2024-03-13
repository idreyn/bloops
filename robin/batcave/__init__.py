try:
    BATCAVE_HOST  # noqa: F821
except:  # noqa: E722
    # You should define this in ../config_secret.py
    BATCAVE_HOST = ("0.0.0.0", 8000)
