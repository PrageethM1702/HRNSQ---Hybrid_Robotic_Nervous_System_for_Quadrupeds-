class ComplementaryIMU:
    def __init__(self, alpha=0.96):
        self.alpha = alpha
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

    def update(self, gyro, accel, dt):
        gx, gy, gz = gyro
        ax, ay, az = accel
        self.roll += gx * dt
        self.pitch += gy * dt
        self.yaw += gz * dt
        accel_roll = ay / max(abs(az), 1e-6)
        accel_pitch = -ax / max(abs(az), 1e-6)
        self.roll = self.alpha * self.roll + (1.0 - self.alpha) * accel_roll
        self.pitch = self.alpha * self.pitch + (1.0 - self.alpha) * accel_pitch
        return {"roll": self.roll, "pitch": self.pitch, "yaw": self.yaw}
