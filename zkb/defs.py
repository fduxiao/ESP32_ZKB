from machine import Pin, I2C, ADC, TouchPad
from neopixel import NeoPixel
import ntptime

from .display import Display
from .music import Music
from .qmi8658 import QMI8658


timezone = 8
ntptime.host = 'ntp.ustc.edu.cn'

pin_p = Pin(27, Pin.IN)
touch_p = TouchPad(pin_p)

pin_y = Pin(14, Pin.IN)
touch_y = TouchPad(pin_y)

pin_t = Pin(12, Pin.IN)
touch_t = TouchPad(pin_t)

pin_h = Pin(13, Pin.IN)
touch_h = TouchPad(pin_h)

pin_o = Pin(15, Pin.IN)
touch_o = TouchPad(pin_o)

pin_n = Pin(4, Pin.IN)
touch_n = TouchPad(pin_n)

touch = {
    'P': pin_p,
    'p': pin_p,
    'Y': pin_y,
    'y': pin_y,
    'T': pin_t,
    't': pin_t,
    'H': pin_h,
    'h': pin_h,
    'O': pin_o,
    'o': pin_o,
    'N': pin_n,
    'n': pin_n,
}

pin_map = [33, 32, 35, 34, 39, 0, 16, 17, 26, 25, 36, 2, 18, 19, 21, 5, None, None, 22, 23]

p0 = Pin(33)
p1 = Pin(32)
p2 = Pin(35)
p3 = Pin(34)
p4 = Pin(39)
p5 = Pin(0)
p6 = Pin(16)
p7 = Pin(17)
p8 = Pin(26)
p9 = Pin(25)
p10 = Pin(36)
p11 = Pin(2)
p13 = Pin(18)
p14 = Pin(19)
p15 = Pin(21)
p16 = Pin(5)

p19 = Pin(22)
p20 = Pin(23)

btn_a = Pin(0, Pin.IN)
btn_b = Pin(2, Pin.IN)
i2c0 = I2C(0, scl=Pin(22), sda=Pin(23))

pixels = NeoPixel(Pin(17, Pin.OUT), 3)

light = ADC(p4)

buzz = p6
music = Music(buzz)

sound = ADC(p10)

oled = Display(128, 64, i2c0)


acc_gyro = QMI8658(i2c0)
