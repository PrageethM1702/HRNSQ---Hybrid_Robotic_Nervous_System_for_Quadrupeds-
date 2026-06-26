from time import sleep
from BMI160_i2c import Driver

bmi = Driver(0x68)

def read_bmi160():
    data = bmi.getMotion6()
    temp_raw = bmi.getTemperature()
    return {
        "gyro_x": data[0],
        "gyro_y": data[1],
        "gyro_z": data[2],
        "accel_x": data[3],
        "accel_y": data[4],
        "accel_z": data[5],
        "temp_raw": temp_raw
    }

if __name__ == "__main__":
    while True:
        vals = read_bmi160()
        print("BMI160:", vals)
        sleep(1)
