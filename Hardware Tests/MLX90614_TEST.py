import time
from smbus2 import SMBus
from adafruit_mlx90614 import MLX90614

i2c_bus = SMBus(1)
sensor = MLX90614(i2c_bus, address=0x5A)

try:
    while True:
        ambient_temp = sensor.ambient_temperature
        object_temp = sensor.object_temperature
        print(f"Ambient Temp: {ambient_temp:.2f} °C")
        print(f"Object Temp: {object_temp:.2f} °C")
        print("-----------------------------")
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
finally:
    i2c_bus.close()
