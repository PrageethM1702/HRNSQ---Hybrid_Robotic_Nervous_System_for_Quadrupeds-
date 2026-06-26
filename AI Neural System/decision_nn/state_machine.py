class DecisionStateMachine:
    def __init__(self):
        self.state = "idle"

    def update(self, telemetry):
        battery = float(telemetry.get("battery_voltage", 12.0))
        risk = float(telemetry.get("risk", 0.0))
        command = telemetry.get("command", "stand")
        if battery < 10.5:
            self.state = "shutdown"
        elif risk > 0.75:
            self.state = "recover"
        elif command == "walk":
            self.state = "locomotion"
        elif command == "explore":
            self.state = "exploration"
        else:
            self.state = "idle"
        return self.state

    def output(self):
        return {
            "idle": {"gait": "stand", "speed": 0.0},
            "locomotion": {"gait": "trot", "speed": 0.35},
            "exploration": {"gait": "walk", "speed": 0.2},
            "recover": {"gait": "crawl", "speed": 0.08},
            "shutdown": {"gait": "stop", "speed": 0.0},
        }[self.state]
