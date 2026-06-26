import random


def gaussian(value, sigma):
    return value + random.gauss(0.0, sigma)


def apply_sensor_noise(sample, sigma=0.01):
    noisy = {}
    for key, value in sample.items():
        noisy[key] = gaussian(float(value), sigma) if isinstance(value, (int, float)) else value
    return noisy
