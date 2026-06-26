"""
Classical HRNS-Q locomotion helpers.

This module is intentionally non-AI: it combines fixed gait phase tables with
2-link inverse kinematics and keeps hip/abduction motors frozen at neutral.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


LEGS = ("FL", "FR", "RL", "RR")


@dataclass(frozen=True)
class LegCommand:
    hip_deg: float
    shoulder_deg: float
    knee_deg: float
    foot_x_cm: float
    foot_y_cm: float
    contact: bool
    pwm_us: int
    enabled: bool = True

    def as_dict(self) -> dict:
        return {
            "hip_deg": round(self.hip_deg, 2),
            "shoulder_deg": round(self.shoulder_deg, 2),
            "knee_deg": round(self.knee_deg, 2),
            "ankle_deg": 0.0,
            "foot_x_cm": round(self.foot_x_cm, 2),
            "foot_y_cm": round(self.foot_y_cm, 2),
            "contact": self.contact,
            "pwm_us": self.pwm_us,
            "enabled": self.enabled,
        }


class FrozenHipLocomotion:
    def __init__(
        self,
        upper_leg_cm: float = 10.0,
        lower_leg_cm: float = 10.5,
        neutral_hip_deg: float = 90.0,
        neutral_shoulder_deg: float = 90.0,
        neutral_knee_deg: float = 90.0,
    ) -> None:
        self.upper_leg_cm = upper_leg_cm
        self.lower_leg_cm = lower_leg_cm
        self.neutral_hip_deg = neutral_hip_deg
        self.neutral_shoulder_deg = neutral_shoulder_deg
        self.neutral_knee_deg = neutral_knee_deg
        self.phase_offsets = {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0}

    def command_frame(self, t: float, gait: str = "stand", speed: float = 0.0) -> dict:
        enabled = gait != "stop"
        if gait in {"stand", "stop"} or speed <= 0.0:
            return {
                leg: LegCommand(
                    hip_deg=self.neutral_hip_deg,
                    shoulder_deg=self.neutral_shoulder_deg,
                    knee_deg=self.neutral_knee_deg,
                    foot_x_cm=0.0,
                    foot_y_cm=-15.0,
                    contact=True,
                    pwm_us=self.angle_to_pwm(self.neutral_shoulder_deg),
                    enabled=enabled,
                ).as_dict()
                for leg in LEGS
            }

        frequency_hz = 1.0 + min(speed, 0.6) * 1.6
        stride_cm = 3.0 + min(speed, 0.6) * 5.0
        lift_cm = 2.0 + min(speed, 0.6) * 3.0
        body_height_cm = -15.0
        frame = {}

        for leg in LEGS:
            phase = (t * frequency_hz + self.phase_offsets[leg]) % 1.0
            if phase < 0.5:
                local = phase / 0.5
                x = stride_cm * (0.5 - local)
                y = body_height_cm
                contact = True
            else:
                local = (phase - 0.5) / 0.5
                x = stride_cm * (local - 0.5)
                y = body_height_cm + lift_cm * math.sin(math.pi * local)
                contact = False

            shoulder, knee = self.inverse_2link(x, y, left_side=leg in {"FL", "RL"})
            frame[leg] = LegCommand(
                hip_deg=self.neutral_hip_deg,
                shoulder_deg=shoulder,
                knee_deg=knee,
                foot_x_cm=x,
                foot_y_cm=y,
                contact=contact,
                pwm_us=self.angle_to_pwm(shoulder),
                enabled=enabled,
            ).as_dict()
        return frame

    def inverse_2link(self, x_cm: float, y_cm: float, left_side: bool = False) -> tuple[float, float]:
        a1 = self.upper_leg_cm
        a2 = self.lower_leg_cm
        distance = math.hypot(x_cm, y_cm)
        distance = max(1.0, min(distance, a1 + a2 - 0.01))
        cos_knee = (distance * distance - a1 * a1 - a2 * a2) / (2.0 * a1 * a2)
        cos_knee = max(-1.0, min(1.0, cos_knee))
        knee_rad = math.acos(cos_knee)

        shoulder_rad = math.atan2(y_cm, x_cm) - math.atan2(
            a2 * math.sin(knee_rad),
            a1 + a2 * math.cos(knee_rad),
        )
        shoulder_deg = 90.0 + math.degrees(shoulder_rad)
        knee_deg = 180.0 - math.degrees(knee_rad)

        if left_side:
            shoulder_deg = 180.0 - shoulder_deg

        return self.clamp_angle(shoulder_deg), self.clamp_angle(knee_deg)

    @staticmethod
    def clamp_angle(angle: float) -> float:
        return max(0.0, min(180.0, angle))

    @staticmethod
    def angle_to_pwm(angle: float) -> int:
        return int(500 + FrozenHipLocomotion.clamp_angle(angle) * (2000.0 / 180.0))


def build_locomotion_frame(t: float, gait: str, speed: float) -> dict:
    return FrozenHipLocomotion().command_frame(t, gait, speed)
