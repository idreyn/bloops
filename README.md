# Installing from scratch on a new Raspberry Pi

You'll need:
- A Raspberry Pi
- A MicroSD card (16 GB should be plenty)
- The [HifiBerry DAC+ ADC Pro](https://www.hifiberry.com/shop/boards/hifiberry-dac-adc-pro/)

## Installing the OS

Grab the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and pop in your SD card. You'll want the 64-bit version of Raspbian for your Pi 4/5/whatever. Make sure you choose the **Edit Settings** option before proceeding. You'll want to change the following:

- The hostname: you'll use this to access the Pi on the local network. We commonly call it `robin`, but if there's an existing device with that name floating around, you'll want to call it something else.
- A username and password. We usually use the username `robin`.
- The Wi-Fi SSID, password, and locale that you want the Pi to connect to when it boots
- The local timezone and keyboard layout
- **Make sure to enable SSH from the Services** tab.

<img width="651" alt="Screenshot 2024-03-13 at 12 22 11 PM" src="https://github.com/robin-labs/robin/assets/2208769/2c653bbd-de1b-4828-8390-a252b47e2ab7">

The installer will install Raspbian on the SD card. Insert it into the Pi and turn it on. To connect for the first time, use:

```
ssh (username)@(hostname).local
```

Above, we chose `robin` for both the `username` and `hostname`, so we connect using `ssh robin@robin.local`. You will be prompted for your password. You'll probably want to follow [these instructions](https://www.raspberrypi.com/documentation/computers/remote-access.html#manually-configure-an-ssh-key) so you can log in without a password in the future.

## Installing the Robin software

First, download OS-level libraries that Robin depends on. In particular, you'll need [Poetry](https://python-poetry.org/) to manage our Python code, and [pipx](https://pipx.pypa.io/stable/installation/) to install Poetry:

```
sudo apt-get install pipx libasound2-dev npm
pipx ensurepath
pipx install poetry
```

You will need to open a new shell (for instance by reconnecting via SSH) before `poetry` becomes available. Then you can install this repo:

- Use `git clone https://github.com/robin-labs/robin.git` if you know you won't need to push your changes back to this repo
- Use `git@github.com:robin-labs/robin.git` if you have permission to commit to this repo. Follow [these](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) instructions to add an SSH key to the Pi (not to your own machine) so you can push code directly from the Pi.

Now run a few install scripts:

```
# Enter the repo
cd robin
# Install Python dependencies
poetry install
# Install our stuff to the OS: device overlay, systemd service, etc.
poetry run rpi-install
```

If `poetry install` hangs, try [adding this variable to your shell](https://askubuntu.com/a/58828):

```
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

Now run `sudo reboot` to restart your Pi. Then, if you run `arecord -l`, you should see the HifiBerry sound card registered as an audio device:

```
**** List of CAPTURE Hardware Devices ****
card 2: sndrpihifiberry [snd_rpi_hifiberry_dacplusadcpro], device 0: HiFiBerry DAC+ADC Pro HiFi multicodec-0 [HiFiBerry DAC+ADC Pro HiFi multicodec-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

Now you should be able to start the Robin software:

```
cd robin
poetry run start
```

## Starting Robin on boot

The installation script registers a [`systemd`](https://systemd.io/) service called `robin.service`. You can use this to automatically start the Robin software when the Pi boots:

```
# Run Robin as a service
sudo systemctl start robin

# Set up to run on boot
sudo systemctl enable robin

# See the logs from the Robin service
journalctl -u robin
```

The `start`, `stop`, `restart`, `enable`, and `disable` commands are all available through `systemctl`.
