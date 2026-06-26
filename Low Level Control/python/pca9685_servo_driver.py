"""
Raspberry Pi PCA9685 servo output for HRNS-Q.

Requires:
    pip install adafruit-blinka adafruit-circuitpython-servokit
"""

from __future__ import annotations

import time

from adafruit_servokit import ServoKit

from hrnsq_locomotion import FrozenHipLocomotion


SERVO_CHANNELS = {
    "FL": {"shoulder": 0, "knee": 1},
    "FR": {"shoulder": 2, "knee": 3},
    "RL": {"shoulder": 4, "knee": 5},
    "RR": {"shoulder": 6, "knee": 7},
}


class PCA9685ServoOutput:
    def __init__(self, channels: int = 16, pulse_min: int = 500, pulse_max: int = 2500) -> None:
        self.kit = ServoKit(channels=channels)
        for mapping in SERVO_CHANNELS.values():
            for channel in mapping.values():
                self.kit.servo[channel].set_pulse_width_range(pulse_min, pulse_max)

    def apply_frame(self, frame: dict) -> None:
        for leg, joints in SERVO_CHANNELS.items():
            command = frame[leg]
            self.kit.servo[joints["shoulder"]].angle = command["shoulder_deg"]
            self.kit.servo[joints["knee"]].angle = command["knee_deg"]

    def neutral(self) -> None:
        for mapping in SERVO_CHANNELS.values():
            self.kit.servo[mapping["shoulder"]].angle = 90
            self.kit.servo[mapping["knee"]].angle = 90


def demo_walk(seconds: float = 5.0) -> None:
    locomotion = FrozenHipLocomotion()
    output = PCA9685ServoOutput()
    start = time.monotonic()
    while time.monotonic() - start < seconds:
        t = time.monotonic() - start
        frame = locomotion.command_frame(t=t, gait="trot", speed=0.25)
        output.apply_frame(frame)
        time.sleep(0.04)
    output.neutral()


if __name__ == "__main__":
    demo_walk()
