This is the Python code that actually runs on the device. To get it running, you'll need to run the following from the ROOT of the repository:

    $ python robin/noisereduce/setup.py build_ext --inplace

You'll also need to create a `config_secret.py` file:

    $ touch robin/config_secret.py

If you want to be able to control your device remotely with the [Batcave](https://github.com/idreyn/batcave) software, you'll need to feed it the address and port of the server:

    $ echo "BATCAVE_HOST = ('0.0.0.0', 8000)" > robin/config_secret.py

Once you do that, you can run `python robin/main.py`. This starts up the whole thing -- Batcave client, audio devices, processing pipeline -- and listens for input from both Batcave and an attached Bluetooth remote. There are some test scripts that deal with a subset of the functionality in the `robin/testing` directory that might also be useful for debugging.