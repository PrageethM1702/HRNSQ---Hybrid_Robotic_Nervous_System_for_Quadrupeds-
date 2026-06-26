import math
import random


class HRNSQSimEnv:
    def __init__(self, dt=0.02):
        self.dt = dt
        self.reset()

    def reset(self):
        self.time = 0.0
        self.pose = {"x": 0.0, "y": 0.0, "yaw": 0.0, "roll": 0.0, "pitch": 0.0}
        self.velocity = 0.0
        self.energy = 0.0
        return self.observation()

    def observation(self):
        return {
            "time": self.time,
            "pose": dict(self.pose),
            "speed": self.velocity,
            "energy": self.energy,
            "imu": {
                "roll": self.pose["roll"],
                "pitch": self.pose["pitch"],
                "yaw_rate": 0.02 * math.sin(self.time),
            },
        }

    def step(self, action):
        stride = sum(abs(v.get("hip", 0.0)) for v in action.values()) / max(len(action), 1)
        lift = sum(max(0.0, v.get("knee", 0.0)) for v in action.values()) / max(len(action), 1)
        self.velocity = max(0.0, min(1.2, stride + 0.25 * lift))
        self.pose["x"] += self.velocity * self.dt
        self.pose["roll"] = 0.04 * random.uniform(-1.0, 1.0)
        self.pose["pitch"] = 0.04 * random.uniform(-1.0, 1.0)
        self.energy += sum(abs(x) for leg in action.values() for x in (leg.get("hip", 0.0), leg.get("knee", 0.0), leg.get("ankle", 0.0))) * self.dt
        self.time += self.dt
        reward = self.velocity - 0.02 * self.energy - abs(self.pose["roll"])
        done = abs(self.pose["roll"]) > 0.5 or abs(self.pose["pitch"]) > 0.5
        return self.observation(), reward, done, {"velocity": self.velocity}
