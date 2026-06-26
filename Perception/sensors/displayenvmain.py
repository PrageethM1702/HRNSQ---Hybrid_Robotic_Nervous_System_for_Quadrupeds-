import time
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from sensors.bmi160_sensor import read_bmi160
from sensors.bmp280_sensor import read_bmp280
from sensors.mlx90614_sensor import read_mlx90614

i2c = busio.I2C(board.SCL, board.SDA)
WIDTH = 128
HEIGHT = 32
OLED_ADDRESS = 0x3C
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=OLED_ADDRESS)
oled.fill(0)
oled.show()

def display_data():
    bmi = read_bmi160()
    bmp = read_bmp280()
    mlx = read_mlx90614()
    lines = [
        f"GyroX:{bmi['gyro_x']} Y:{bmi['gyro_y']}",
        f"AccelX:{bmi['accel_x']} Y:{bmi['accel_y']}",
        f"Temp:{bmp['temperature']:.1f}C P:{bmp['pressure']:.1f}",
        f"IR:{mlx['object']:.1f}C Amb:{mlx['ambient']:.1f}"
    ]
    oled.fill(0)
    for i, line in enumerate(lines):
        oled.text(line, 0, i*8, 1)
    oled.show()

while True:
    display_data()
    time.sleep(1)
