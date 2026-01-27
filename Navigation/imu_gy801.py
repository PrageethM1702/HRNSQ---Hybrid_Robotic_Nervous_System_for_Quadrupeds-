import smbus2
import time
import math

bus = smbus2.SMBus(1)

ADXL345 = 0x53
L3G4200D = 0x69
HMC5883L = 0x1E
BMP180 = 0x77

def imu_init():
    # ADXL345 (Accelerometer)
    bus.write_byte_data(ADXL345, 0x2D, 0x08)
# L3G4200D (Gyro)
    bus.write_byte_data(L3G4200D, 0x20, 0x0F)
# HMC5883L (Mag)
    bus.write_byte_data(HMC5883L, 0x00, 0x70)
    bus.write_byte_data(HMC5883L, 0x01, 0x20)
    bus.write_byte_data(HMC5883L, 0x02, 0x00)

def read_word(addr, reg):
    low = bus.read_byte_data(addr, reg)
    high = bus.read_byte_data(addr, reg + 1)
    value = (high << 8) | low
    if value > 32767:
        value -= 65536
    return value

def read_accel():
    x = read_word(ADXL345, 0x32)
    y = read_word(ADXL345, 0x34)
    z = read_word(ADXL345, 0x36)
    return x, y, z

def read_gyro():
    x = read_word(L3G4200D, 0x28)
    y = read_word(L3G4200D, 0x2A)
    z = read_word(L3G4200D, 0x2C)
    return x, y, z

def read_mag():
    x = read_word(HMC5883L, 0x03)
    y = read_word(HMC5883L, 0x07)
    z = read_word(HMC5883L, 0x05)
    return x, y, z

def get_imu_data():
    accel = read_accel()
    gyro = read_gyro()
    mag = read_mag()

    return {
        "accel": accel,
        "gyro": gyro,
        "mag": mag
    }

if __name__ == "__main__":
    imu_init()
    while True:
        print(get_imu_data())
        time.sleep(0.1)
