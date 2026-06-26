# I2C Map

| Address | Device | Purpose |
| --- | --- | --- |
| 0x68 | IMU | body acceleration and gyro |
| 0x76 | BMP280 | pressure and environment test |
| 0x5A | MLX90614 | temperature sensing |
| 0x40 | Si7021 | humidity and temperature |
| 0x58 | SGP30 | air quality test module |

Use 3.3 V pull-ups for STM32-connected buses.
