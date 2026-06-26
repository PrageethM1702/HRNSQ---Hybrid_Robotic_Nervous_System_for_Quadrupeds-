import board
import busio
import adafruit_bmp280

i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)

def read_bmp280():
    return {
        "temperature": bmp280.temperature,
        "pressure": bmp280.pressure
    }
