from micropython import const
import struct
import time

QMI8658_ADDR = const(0x6A)
QMI8658_ADDR2 = const(0x6B)

REG_WHO_AM_I = const(0x00)
VAL_SENSOR_ID = const(0x05)

REG_CTRL1 = const(0x02)  # power control
REG_CTRL2 = const(0x03)  # accelerometer config
REG_CTRL3 = const(0x04)  # gyroscope config
REG_CTRL4 = const(0x05)
REG_CTRL5 = const(0x06)
REG_CTRL6 = const(0x07)
REG_CTRL7 = const(0x08)  # enable sensor 

REG_TEMP_L = const(0x33)
REG_TEMP_H = const(0x34)

REG_AX_L = const(0x35)
REG_AX_H = const(0x36)
REG_AY_L = const(0x37)
REG_AY_H = const(0x38)
REG_AZ_L = const(0x39)
REG_AZ_H = const(0x3A)

REG_GX_L = const(0x3B)
REG_GX_H = const(0x3C)
REG_GY_L = const(0x3D)
REG_GY_H = const(0x3E)
REG_GZ_L = const(0x3F)
REG_GZ_H = const(0x40)

REG_RST = const(0x60)
VAL_RST = const(0xB0)

PATTERN_XYZ = const("<hhh")
RESOLUTION = const(1 << (2 * 8))

STANDARD_GRAVITY = const(9.80665)
PI = const(3.1415926535897932)
DEGREE = const(0.01745329)  # PI / 180


class QMI8658:
    def __init__(self, i2c, addr=QMI8658_ADDR2) -> None:
        self.i2c = i2c
        self.addr = addr

        who_am_i = self.who_am_i()
        if who_am_i != VAL_SENSOR_ID:
            raise NotImplementedError("unknown identity", who_am_i)
        
        self.acc_scale = 1
        self.gyro_scale = 1
        self.init()

    def read_byte(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def read_reg(self, reg, length):
        bs = bytearray()
        for i in range(length):
            bs.append(
                self.read_byte(reg + i)
            )
        return bs
    
    def write_byte(self, reg, x):
        return self.i2c.writeto_mem(self.addr, reg, bytearray([x]))
    
    def who_am_i(self):
        return self.read_byte(REG_WHO_AM_I)
    
    def init(self):
        self.reset()
        self.enable()

        # set low-pass filter
        self.write_byte(REG_CTRL5, 0b0_001_0_001)

        self.set_accelerometer_scale()
        self.set_gyroscope_scale()

    def reset(self):
        self.write_byte(REG_RST, VAL_RST)
        time.sleep_ms(10)
        if self.read_byte(0x4D) != 0x80:
            raise RuntimeError("fail to reset QMI8658")

    def set_accelerometer_scale(self, scale=2):
        bits = 0b000
        if scale == 2:
            bits += 0
        elif scale == 4:
            bits += 1
        elif scale == 8:
            bits += 2
        elif scale == 16:
            bits += 3
        else:
            raise ValueError('only 2, 4, 8, 16 g are supported for scale')
        bits <<= 3
        self.write_byte(REG_CTRL2, bits)
        self.acc_scale = RESOLUTION // scale // 2

    def set_gyroscope_scale(self, scale=16):
        bits = 0b000
        if scale == 16:
            bits += 0
        elif scale == 32:
            bits += 1
        elif scale == 64:
            bits += 2
        elif scale == 128:
            bits += 3
        elif scale == 256:
            bits += 4
        elif scale == 512:
            bits += 5
        elif scale == 1024:
            bits += 6
        else:
            raise ValueError('only 16, 32, 64, 128, 256, 512, 1024 degree per second are supported for scale')
        bits <<= 3
        self.write_byte(REG_CTRL3, bits)
        self.gyro_scale = RESOLUTION // scale // 2

    def enable(self):
        data = self.read_byte(REG_CTRL7)
        data |= 0b11
        self.write_byte(REG_CTRL7, data)
    
    def disable(self):
        data = self.read_byte(REG_CTRL7)
        data &= 0b11111100
        self.write_byte(REG_CTRL7, data)

    def read_accelerometer(self, mps2=False):
        bs = self.read_reg(REG_AX_L, 6)
        x, y, z = struct.unpack(PATTERN_XYZ, bs)
        x /= self.acc_scale
        y /= self.acc_scale
        z /= self.acc_scale
        if mps2:
            x *= STANDARD_GRAVITY
            y *= STANDARD_GRAVITY
            z *= STANDARD_GRAVITY
        return x, y, z

    def read_gyproscope(self):
        bs = self.read_reg(REG_GX_L, 6)
        x, y, z = struct.unpack(PATTERN_XYZ, bs)
        
        x /= self.gyro_scale
        y /= self.gyro_scale
        z /= self.gyro_scale

        x *= DEGREE
        y *= DEGREE
        z *= DEGREE

        return x, y, z
