import board
import busio
import adafruit_si7021

i2c = busio.I2C(board.SCL, board.SDA)
si7021 = adafruit_si7021.SI7021(i2c)

def read_si7021():
    return {
        "temperature": si7021.temperature,
        "humidity": si7021.relative_humidity
    }
