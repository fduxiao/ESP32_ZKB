from ssd1306 import SSD1306_I2C


class Display(SSD1306_I2C):
    def __init__(self, width, height, i2c, addr=0x3C):
        super().__init__(width, height, i2c, addr)

    def draw_xyz(self, func):
        while True:
            x, y, z = func()
            self.fill(0)
            self.text(f'x: {x}', 0, 0)
            self.text(f'y: {y}', 0, 10)
            self.text(f'z: {z}', 0, 20)
            d = (x * x + y * y + z * z) ** 0.5
            self.text(f'd: {d}', 0, 30)
            self.show()
