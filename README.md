# Robin

Robin is an echolocation headset; it is a research platform, and a prototype mobility aid for blind people. It is the spiritual successor to the [Sonic Eye](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4536767/) (Sohl-Dickstein et al., 2015). This repository and this README focus on the _code_ for the device; schematics for the hardware are in other repos in this Github organization. But for the curious, the device currently looks like this:

<img src="https://github.com/robin-labs/robin/assets/2208769/0d185afb-1f4f-41ba-8dcc-24892ee6839d" alt="The Robin device: a headset on a dummy head, wired up to a Raspberry Pi in a carrying case" height="200">

The code is written in Python and is designed to run on a Raspberry Pi.

## Installing from scratch

*You can skip this section if you already have a working device.*

You'll need:
- A Raspberry Pi 4
- A MicroSD card (16 GB should be plenty)
- The [HifiBerry DAC+ ADC Pro](https://www.hifiberry.com/shop/boards/hifiberry-dac-adc-pro/)

Grab the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and pop in your SD card. You'll want the 64-bit version of Raspbian for your Pi. Make sure you choose the **Edit Settings** option before proceeding. You'll want to change the following:

- The hostname: you'll use this to access the Pi on the local network. We commonly call it `robin`, but if there's an existing device with that name floating around, you'll want to call it something else.
- A username and password. We usually use the username `robin`.
- The Wi-Fi SSID, password, and locale that you want the Pi to connect to when it boots
- The local timezone and keyboard layout
- **Make sure to enable SSH from the Services** tab.

<img width="651" alt="screenshot of the the RPi imager tool" src="https://github.com/robin-labs/robin/assets/2208769/2c653bbd-de1b-4828-8390-a252b47e2ab7">

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

Recordings will be saved to the `~/recordings` directory.

After you `sudo reboot`, the device should work without further intervention from the command line.

## Controlling the Robin service

The installation script registers a [`systemd`](https://systemd.io/) service called `robin.service`. It will automatically start Robin on boot (if the headset is connected and powered on, you'll hear three clicks from the emitters when it comes online). You can view the output using `journalctl`:

```
journalctl -u robin -f
```

You can use the `start`, `stop`, `restart`, `enable`, and `disable` commands from `systemctl` to manage the service, e.g.

```
sudo systemctl restart robin
```

## Using the `batcave` web remote

Robin ships with a helpful web interface for debugging and testing (see the `batcave_server` directory). By default, the Robin service will start the server. Assuming you're connected to the same Wi-Fi network as Robin, you can visit `http://robin.local:8000` to visit the remote (assuming the hostname is `robin` — you may have chosen something else). It has three tabs:

- `Emit` is a big button that will emit the currently configured pulse and stream it through your browser
- `Config` provides a frontend to `config.json` (see the section below) and lets you control many important settings, particularly the output pulse
- `Logs` shows debug logs streaming from the device.

## The `config.json` file

Many important settings are specified in `config.json` at the root of the repository. It is not checked into source, but the `poetry run install-rpi` command should install a basic `config.json` for you to use. The available settings are specified by Pydantic models in `robin/config.py`, and these are mirrored in `config.schema.json` which should give you good autocomplete support in an IDE like VSCode:

<img width="400" alt="config.json being edited in vscode" src="https://github.com/robin-labs/robin/assets/2208769/b3b36e8a-a11e-4fcd-973c-1bbc3f044971">

This lets you control settings like:

- The currently emitted pulse
- A bluetooth remote to connect to, and a mapping of `remote_keys` to pulses
- Key echolocation settings, for instance the `slowdown`, and gain calibration options for the microphones
- Which recordings are saved from each pulse
