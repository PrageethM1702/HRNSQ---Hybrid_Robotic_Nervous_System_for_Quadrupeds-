import random


def randomize_domain(config=None):
    config = dict(config or {})
    config["mass_scale"] = random.uniform(0.85, 1.15)
    config["friction"] = random.uniform(0.45, 1.2)
    config["motor_strength"] = random.uniform(0.8, 1.1)
    config["sensor_delay_ms"] = random.randint(0, 30)
    return config
