import board
import busio
import adafruit_sgp30

i2c = busio.I2C(board.SCL, board.SDA)
sgp30 = adafruit_sgp30.SGP30(i2c, address=0x58)

def read_sgp30():
    return {
        "tvoc": sgp30.tvoc,
        "eco2": sgp30.eco2
    }
