import math


LEGS = ("FL", "FR", "RL", "RR")


class GaitModel:
    def __init__(self, gait="trot", frequency=1.4, amplitude=0.35):
        self.gait = gait
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase_offsets = {
            "walk": {"FL": 0.0, "FR": 0.5, "RL": 0.75, "RR": 0.25},
            "trot": {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0},
            "pace": {"FL": 0.0, "FR": 0.5, "RL": 0.0, "RR": 0.5},
            "bound": {"FL": 0.0, "FR": 0.0, "RL": 0.5, "RR": 0.5},
        }

    def predict(self, state):
        t = float(state.get("time", 0.0))
        speed = max(0.0, float(state.get("speed", 0.25)))
        terrain_gain = float(state.get("terrain_gain", 1.0))
        phases = self.phase_offsets.get(self.gait, self.phase_offsets["trot"])
        commands = {}
        for leg in LEGS:
            phase = (t * self.frequency + phases[leg]) % 1.0
            lift = max(0.0, math.sin(2.0 * math.pi * phase))
            swing = math.sin(2.0 * math.pi * phase)
            commands[leg] = {
                "hip": round(speed * 0.45 * math.cos(2.0 * math.pi * phase), 4),
                "knee": round(self.amplitude * terrain_gain * lift, 4),
                "ankle": round(-0.5 * self.amplitude * swing, 4),
                "contact": phase > 0.5,
            }
        return commands


def load_model(path=None):
    return GaitModel()
