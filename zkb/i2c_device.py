import struct


class RegByte:
    def __init__(self, reg) -> None:
        self.reg = reg

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.read_byte(self.reg)
    
    def __set__(self, instance, value):
        instance.write_byte(self.reg, value)


class RegStructure:
    def __init__(self, reg, pattern) -> None:
        self.reg = reg
        self.pattern = pattern
        self.length = struct.calcsize(pattern)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        bs = instance.read_reg(self.reg, self.length)
        return struct.unpack(self.pattern, bs)


class I2CDevice:
    def __init__(self, i2c, addr) -> None:
        self.i2c =i2c
        self.addr = addr

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
