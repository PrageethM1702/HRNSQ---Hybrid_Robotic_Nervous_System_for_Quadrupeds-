class FaultDetector:
    def __init__(self):
        self.limits = {
            "battery_min": 10.5,
            "logic_min": 3.0,
            "logic_max": 3.6,
            "temperature_max": 70.0,
            "tilt_max": 45.0,
            "reflex_timeout": 0.1,
        }

    def evaluate(self, telemetry):
        faults = []
        if telemetry.get("battery_voltage", 12.0) <= self.limits["battery_min"]:
            faults.append("battery_low")
        logic = telemetry.get("logic_voltage", 3.3)
        if logic < self.limits["logic_min"] or logic > self.limits["logic_max"]:
            faults.append("logic_voltage")
        if telemetry.get("temperature_c", 25.0) >= self.limits["temperature_max"]:
            faults.append("over_temperature")
        if abs(telemetry.get("tilt_deg", 0.0)) >= self.limits["tilt_max"]:
            faults.append("tilt")
        if telemetry.get("reflex_age_s", 0.0) >= self.limits["reflex_timeout"]:
            faults.append("reflex_signal_timeout")
        if telemetry.get("gpio_voltage", 3.3) > 3.6:
            faults.append("unsafe_gpio_voltage")
        return faults


def is_safe(telemetry):
    return len(FaultDetector().evaluate(telemetry)) == 0
