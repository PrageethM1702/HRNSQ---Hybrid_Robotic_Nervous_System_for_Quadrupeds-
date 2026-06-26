import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c, address=0x48)
chan = AnalogIn(ads, ADS1115.P0)

def read_dust():
    return {
        "raw": chan.value,
        "voltage": chan.voltage
    }
