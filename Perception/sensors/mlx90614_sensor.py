import board
import busio
import adafruit_mlx90614

i2c = busio.I2C(board.SCL, board.SDA)
mlx = adafruit_mlx90614.MLX90614(i2c)

def read_mlx90614():
    return {
        "ambient": mlx.ambient_temperature,
        "object": mlx.object_temperature
    }
