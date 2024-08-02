from machine import PWM
import time
import asyncio


class Music:
    def __init__(self, buzz) -> None:
        self.buzz = buzz
        self.pwm = None

    def pwm(self, freq, duty=None, duty_u16=None, duty_ns=None):
        if duty is not None:
            self.pwm = PWM(self.buzz, freq=freq, duty=duty)
        elif duty_u16 is not None:
            self.pwm = PWM(self.buzz, freq=freq, duty_u16=duty_u16)
        elif duty_ns is not None:
            self.pwm = PWM(self.buzz, freq=freq, duty_ns=duty_ns)
        else:
            self.pwm = PWM(self.buzz, freq=freq, duty=0)

    def deinit(self):
        if self.pwm is not None:
            self.pwm.deinit()
            self.pwm = None

    stop = deinit

    def pitch(self, freq, duration_ms=50, volume=512):
        self.pwm(freq, volume)
        time.sleep_ms(duration_ms)
        self.stop()

    async def pitch_async(self, freq, duration_ms=50, volume=512):
        self.pwm(freq, volume)
        await asyncio.sleep_ms(duration_ms)
        self.stop()
