from micropython import const
import time
from .i2c_device import I2CDevice, RegStructure, RegByte


MMC5983_ADDR = const(0x30)
MMC5983_HALF_RANGE = const((1 << 18) // 2)


class MMC5983(I2CDevice):
    CM_OFF = const(0b000)
    CM_1HZ = const(0b001)
    CM_10HZ = const(0b010)
    CM_20HZ = const(0b011)
    CM_50HZ = const(0b100)
    CM_100HZ = const(0b101)
    CM_200HZ = const(0b110)
    CM_1000HZ = const(0b111)
    frequency_values = (
        CM_OFF,
        CM_1HZ,
        CM_10HZ,
        CM_20HZ,
        CM_50HZ,
        CM_100HZ,
        CM_200HZ,
        CM_1000HZ,
    )

    BW_100HZ = const(0b00)
    BW_200HZ = const(0b01)
    BW_400HZ = const(0b10)
    BW_800HZ = const(0b11)
    bandwidth_values = (BW_100HZ, BW_200HZ, BW_400HZ, BW_800HZ)

    xyz_out01 = RegStructure(0x00, '<HHH')
    xyz_out2 = RegByte(0x06)
    temp_out = RegByte(0x07)
    status = RegByte(0x08)

    ctrl0 = RegByte(0x09, 0)

    ctrl1 = RegByte(0x0A, 0)
    bandwidth = ctrl1[1:0]
    sw_rst = ctrl1[7]

    ctrl2 = RegByte(0x0B, 0)
    cm_freq = ctrl2[2:0]
    cm_enable = ctrl2[3]

    ctrl3 = RegByte(0x0C, 0)

    prod_id = RegByte(0x2F)

    def __init__(self, i2c, addr=MMC5983_ADDR) -> None:
        super().__init__(i2c, addr)

        prod_id = self.prod_id()
        if prod_id != 0x30:
            raise RuntimeError(f'Unknown device: 0x{prod_id:02X}')

        self.init()

    def soft_reset(self):
        self.sw_rst(1)
        time.sleep_ms(10)

    def continuous(self):
        self.cm_enable(1)

    def one_shot(self):
        self.cm_enable(0)

    def set_freq(self, freq):
        if freq not in self.frequency_values:
            raise ValueError('unknown frequency', freq)

        if freq == self.CM_200HZ and self.bandwidth.value < self.BW_200HZ:
            raise RuntimeError("bandwidth cannot be less than 200HZ")
        if freq == self.CM_1000HZ and self.bandwidth.value < self.BW_800HZ:
            raise RuntimeError("bandwidth cannot be less than 800HZ")

        self.one_shot()
        self.cm_freq = freq
        self.continuous()

    def set_bandwidth(self, bandwith):
        if bandwith not in self.bandwidth_values:
            raise ValueError('unknown bandwith', bandwith)

        self.one_shot()
        self.bandwidth = bandwith
        self.continuous()

    def init(self):
        self.soft_reset()
        self.set_bandwidth(self.BW_400HZ)
        self.set_freq(self.CM_200HZ)

    def read_xyz_raw(self):
        x, y, z = self.xyz_out01()
        extra = self.xyz_out2()

        x = x << 2 | (((extra & 0b11_00_00_00) >> 6) & 0b11)
        y = y << 2 | (((extra & 0b00_11_00_00) >> 4) & 0b11)
        z = z << 2 | (((extra & 0b00_00_11_00) >> 2) & 0b11)

        return x, y, z

    def read_xyz(self):
        x, y, z = self.read_xyz_raw()

        x = (x - MMC5983_HALF_RANGE) / MMC5983_HALF_RANGE
        y = (y - MMC5983_HALF_RANGE) / MMC5983_HALF_RANGE
        z = (z - MMC5983_HALF_RANGE) / MMC5983_HALF_RANGE

        return x, y, z
