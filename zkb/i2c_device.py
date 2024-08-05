import struct


def cal_mask(key):
    if isinstance(key, int):
        hight = key
        low = key
    elif isinstance(key, slice):
        hight = key.start
        low = key.stop
    else:
        raise KeyError('unknown key', key)
    length = hight - low + 1
    mask = 2 ** length - 1
    mask <<= low
    return low, mask


class ByteWrapper:
    def __init__(self, device, reg, value=None) -> None:
        self.device = device
        self.reg = reg
        self.value = value

    def read(self):
        value = self.device.read_byte(self.reg)
        self.value = value
        return self

    def write(self, value=None):
        if value is None:
            value = self.value
            if value is None:
                value = self.read()
        self.device.write_byte(self.reg, value)
        return self

    def set(self, mask, value):
        value &= mask
        mask ^= 0b1111_1111
        value |= mask & self.value
        self.value = value
        return self

    def __call__(self, value=None):
        if value is None:
            self.read()
            return self.value
        return self.write(value)

    def __getitem__(self, key):
        shift, mask = cal_mask(key)
        value = self.value & mask
        value >>= shift
        return value

    def __setitem__(self, key, value):
        shift, mask = cal_mask(key)
        self.set(mask, value << shift)
        self.write()


class SliceWrapper:
    def __init__(self, wrapper: ByteWrapper, shift, mask) -> None:
        self.wrapper = wrapper
        self.shift = shift
        self.mask = mask

    def read(self):
        self.wrapper.read()
        return self

    def write(self, value):
        self.wrapper.set(self.mask, value << self.shift)
        self.wrapper.write()
        return self

    @property
    def value(self):
        if self.wrapper.value is None:
            self.wrapper.read()
        value = self.wrapper.value
        value &= self.mask
        value >>= self.shift
        return value

    def __call__(self, value=None):
        if value is None:
            return self.value
        return self.write(value)


class RegSlice:
    def __init__(self, prop, item) -> None:
        self.prop = prop
        self.item = item

    def __get__(self, instance, owner):
        if instance is None:
            return self
        shift, mask = cal_mask(self.item)
        prop = self.prop.__get__(instance, owner)
        return SliceWrapper(prop, shift, mask)

    def __set__(self, instance, value):
        if instance is None:
            return self
        prop = self.prop.__get__(instance, None)
        return prop.__setitem__(self.item, value)


class RegByte:
    def __init__(self, reg, default=None) -> None:
        self.reg = reg
        self.default = default
        self.wrapper = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.wrapper is None:
            self.wrapper = ByteWrapper(instance, self.reg, self.default)
        return self.wrapper
    
    def __set__(self, instance, value):
        instance.write_byte(self.reg, value)

    def __getitem__(self, item):
        return RegSlice(self, item)


class RegStructure:
    def __init__(self, reg, pattern) -> None:
        self.reg = reg
        self.pattern = pattern
        self.length = struct.calcsize(pattern)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        bs = instance.read_reg(self.reg, self.length)
        return lambda: struct.unpack(self.pattern, bs)


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
