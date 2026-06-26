class SensorFusionModel:
    def __init__(self):
        self.weights = {
            "imu": 0.35,
            "pressure": 0.25,
            "vision": 0.25,
            "temperature": 0.05,
            "power": 0.10,
        }

    def predict(self, sample):
        stability = 1.0
        stability -= abs(float(sample.get("roll", 0.0))) * self.weights["imu"]
        stability -= abs(float(sample.get("pitch", 0.0))) * self.weights["imu"]
        stability += min(1.0, float(sample.get("foot_contact_ratio", 0.0))) * self.weights["pressure"]
        stability -= min(1.0, float(sample.get("obstacle_distance_risk", 0.0))) * self.weights["vision"]
        stability -= max(0.0, float(sample.get("motor_temp", 35.0)) - 55.0) * 0.01 * self.weights["temperature"]
        stability -= max(0.0, 11.1 - float(sample.get("battery_voltage", 12.0))) * self.weights["power"]
        stability = max(0.0, min(1.0, stability))
        return {
            "stability": round(stability, 4),
            "risk": round(1.0 - stability, 4),
            "mode": "normal" if stability > 0.65 else "careful" if stability > 0.35 else "stop",
        }
