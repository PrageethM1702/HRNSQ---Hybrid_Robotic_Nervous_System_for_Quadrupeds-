import numpy as np
import time

class NavigationEKF:
    def __init__(self):
        self.x = np.zeros((9, 1))
        self.P = np.eye(9) * 0.1
        self.Q = np.eye(9) * 0.01
        self.R_gps = np.eye(4) * 2.0
        self.R_baro = np.array([[1.5]])
        self.last_t = time.time()

    def pressure_to_altitude(self, pressure_hpa):
        return 44330.0 * (1.0 - (pressure_hpa / 1013.25) ** 0.1903)

    def predict(self, accel, gyro):
        t = time.time()
        dt = t - self.last_t
        self.last_t = t

        ax, ay, az = accel
        gx, gy, gz = gyro

        roll, pitch, yaw = self.x[3:6, 0]

        self.x[3,0] += gx * dt
        self.x[4,0] += gy * dt
        self.x[5,0] += gz * dt

        self.x[6,0] += ax * dt
        self.x[7,0] += ay * dt
        self.x[8,0] += az * dt

        self.x[0,0] += self.x[6,0] * dt
        self.x[1,0] += self.x[7,0] * dt
        self.x[2,0] += self.x[8,0] * dt

        F = np.eye(9)
        for i in range(3):
            F[i, i+6] = dt

        self.P = F @ self.P @ F.T + self.Q

    def update_gps(self, gps):
        z = np.array([
            gps["latitude"],
            gps["longitude"],
            gps["velocity_x"],
            gps["velocity_y"]
        ]).reshape((4,1))

        H = np.zeros((4,9))
        H[0,0] = 1
        H[1,1] = 1
        H[2,6] = 1
        H[3,7] = 1

        y = z - H @ self.x
        S = H @ self.P @ H.T + self.R_gps
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x += K @ y
        self.P = (np.eye(9) - K @ H) @ self.P

    def update_baro(self, pressure):
        alt = self.pressure_to_altitude(pressure)
        z = np.array([[alt]])

        H = np.zeros((1,9))
        H[0,2] = 1

        y = z - H @ self.x
        S = H @ self.P @ H.T + self.R_baro
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x += K @ y
        self.P = (np.eye(9) - K @ H) @ self.P

    def get_nav(self):
        return {
            "roll": self.x[3,0],
            "pitch": self.x[4,0],
            "heading": self.x[5,0],
            "velocity_x": self.x[6,0],
            "velocity_y": self.x[7,0],
            "altitude": self.x[2,0]
        }
