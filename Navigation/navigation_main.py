import time
from imu_gy801 import imu_init, get_imu_data
from gps_neo_m8n import get_gps_data

def main():
    imu_init()
    print("HRNS-Q Navigation System Started")

    while True:
        imu = get_imu_data()
        gps = get_gps_data()

        print("- NAV DATA -")
        print(f"Accel: {imu['accel']}")
        print(f"Gyro : {imu['gyro']}")
        print(f"Mag  : {imu['mag']}")
        print(f"GPS  : {gps}")
        print("-.....................-\n")

        time.sleep(0.2)

if __name__ == "__main__":
    main()
