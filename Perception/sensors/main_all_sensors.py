import time
from bmi160_sensor import read_bmi160
from sgp30_sensor import read_sgp30
from bmp280_sensor import read_bmp280
from si7021_sensor import read_si7021
from mlx90614_sensor import read_mlx90614
from dust_sensor import read_dust

print("starting sensor readings...")

while True:
    data = {}

    data["BMI160"] = read_bmi160()
    data["SGP30"] = read_sgp30()
    data["BMP280"] = read_bmp280()
    data["Si7021"] = read_si7021()
    data["MLX90614"] = read_mlx90614()
    data["Dust"] = read_dust()

    print(" SENSOR DATA:___")
    for sensor, vals in data.items():
        print(f"{sensor}: {vals}")
    print("---\n")

    time.sleep(1)
