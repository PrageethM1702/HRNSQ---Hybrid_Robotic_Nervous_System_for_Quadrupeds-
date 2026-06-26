import time
from navigation_estimator import NavigationEKF
from bmi160_sensor import read_bmi160
from bmp280_sensor import read_bmp280
from sgp30_sensor import read_sgp30
from si7021_sensor import read_si7021
from mlx90614_sensor import read_mlx90614
from dust_sensor import read_dust
from gps_neo6m import read_gps

ekf = NavigationEKF()

while True:
    bmi = read_bmi160()
    bmp = read_bmp280()
    gps = read_gps()

    accel = (
        bmi["accel_x"] * 0.001,
        bmi["accel_y"] * 0.001,
        bmi["accel_z"] * 0.001
    )

    gyro = (
        bmi["gyro_x"] * 0.001,
        bmi["gyro_y"] * 0.001,
        bmi["gyro_z"] * 0.001
    )

    ekf.predict(accel, gyro)

    if bmp:
        ekf.update_baro(bmp["pressure"])

    if gps:
        gps["velocity_x"] = ekf.x[6,0]
        gps["velocity_y"] = ekf.x[7,0]
        ekf.update_gps(gps)

    nav = ekf.get_nav()

    print("NAV", nav)

    if gps:
        print("GPS", gps)

    print("BMP280", bmp)
    print("SGP30", read_sgp30())
    print("SI7021", read_si7021())
    print("MLX90614", read_mlx90614())
    print("Dust", read_dust())

    print("----")
    time.sleep(0.5)
