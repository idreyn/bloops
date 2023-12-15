import smbus

I2C_INDEX = 1
I2C_ADDRESS = 0x2C
VALID_CHANNELS = [0, 1]
CHANNEL_ADDRESSES = [0x01, 0x03]
WIPER_POSITIONS = 256
KOHM_MAX_RESISTANCE = 10
BYTE_TO_OHMS = KOHM_MAX_RESISTANCE / WIPER_POSITIONS


class AD5252(object):
    def __init__(self):
        self.bus = smbus.SMBus(I2C_INDEX)

    def write(self, kohm_resistance, channel):
        assert channel in VALID_CHANNELS
        assert 0 <= kohm_resistance <= KOHM_MAX_RESISTANCE
        if kohm_resistance in (int(KOHM_MAX_RESISTANCE), float(KOHM_MAX_RESISTANCE)):
            # 10 causes a rollover to the min value
            # Set it to close to 10 instead
            kohm_resistance = 9.9
        write_out = int(kohm_resistance / BYTE_TO_OHMS)
        self.bus.write_i2c_block_data(
            I2C_ADDRESS, CHANNEL_ADDRESSES[channel], [write_out]
        )

    def write_all(self, kohm_resistance):
        for chan in VALID_CHANNELS:
            self.write(kohm_resistance, chan)

    def read(self, channel):
        assert channel in VALID_CHANNELS
        return (
            self.bus.read_byte_data(I2C_ADDRESS, CHANNEL_ADDRESSES[channel])
            * BYTE_TO_OHMS
        )

    def read_all(self):
        return [self.read(chan) for chan in VALID_CHANNELS]
