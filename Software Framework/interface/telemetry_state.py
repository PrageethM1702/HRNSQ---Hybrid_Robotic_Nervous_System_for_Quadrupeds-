import base64
import math
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path


LOW_LEVEL_PYTHON = Path(__file__).resolve().parents[2] / "Low Level Control" / "python"
if LOW_LEVEL_PYTHON.exists() and str(LOW_LEVEL_PYTHON) not in sys.path:
    sys.path.insert(0, str(LOW_LEVEL_PYTHON))

from hrnsq_locomotion import build_locomotion_frame


LEGS = ("FL", "FR", "RL", "RR")


@dataclass
class RobotState:
    timestamp: float = 0.0
    mode: str = "idle"
    gait: str = "stand"
    command: str = "stand"
    speed: float = 0.0
    uptime_s: float = 0.0
    battery_voltage: float = 12.1
    battery_percent: float = 86.0
    logic_voltage: float = 3.31
    current_a: float = 0.8
    power_w: float = 9.7
    temperature_c: float = 34.0
    humidity_percent: float = 54.0
    air_quality_eco2: int = 450
    object_temp_c: float = 31.0
    gps: dict = field(default_factory=dict)
    imu: dict = field(default_factory=dict)
    accelerometer: dict = field(default_factory=dict)
    gyroscope: dict = field(default_factory=dict)
    magnetometer: dict = field(default_factory=dict)
    attitude: dict = field(default_factory=dict)
    foot_pressure: dict = field(default_factory=dict)
    reflex: dict = field(default_factory=dict)
    cpg: dict = field(default_factory=dict)
    vision: dict = field(default_factory=dict)
    camera: dict = field(default_factory=dict)
    navigation: dict = field(default_factory=dict)
    ai: dict = field(default_factory=dict)
    communication: dict = field(default_factory=dict)
    safety: dict = field(default_factory=dict)
    actuators: dict = field(default_factory=dict)
    logs: list = field(default_factory=list)


class TelemetryState:
    def __init__(self):
        self.started = time.time()
        self.state = RobotState()
        self.sequence = 0
        self.command = "stand"
        self.base_lat = 6.927079
        self.base_lon = 79.861244
        self.logs = []

    def set_command(self, command):
        if command in {"stand", "walk", "explore", "recover", "shutdown"}:
            self.command = command
            self.add_log("command", command)

    def add_log(self, level, message):
        self.logs.append({"time": time.strftime("%H:%M:%S"), "level": level, "message": message})
        self.logs = self.logs[-30:]

    def ingest(self, packet):
        if "command" in packet:
            self.set_command(str(packet["command"]))
        data = asdict(self.state)
        for key, value in packet.items():
            if key in data and key != "logs":
                data[key] = value
        self.state = RobotState(**data)
        return self.snapshot()

    def snapshot(self):
        now = time.time()
        t = now - self.started
        self.sequence += 1
        mode, gait, speed = self._mode_gait_speed()
        risk = self._risk(t)
        lat = self.base_lat + math.sin(t / 120.0) * 0.00015
        lon = self.base_lon + math.cos(t / 140.0) * 0.00015
        accel = {
            "x": round(math.sin(t * 1.7) * 0.18, 3),
            "y": round(math.cos(t * 1.3) * 0.12, 3),
            "z": round(9.81 + math.sin(t * 2.1) * 0.08, 3),
            "unit": "m/s2",
        }
        gyro = {
            "x": round(math.sin(t * 0.9) * 1.4, 3),
            "y": round(math.cos(t * 0.7) * 1.1, 3),
            "z": round(math.sin(t * 0.4) * 2.2, 3),
            "unit": "deg/s",
        }
        attitude = {
            "roll": round(math.sin(t * 0.6) * 3.8, 2),
            "pitch": round(math.cos(t * 0.5) * 2.8, 2),
            "yaw": round((t * 4.0) % 360.0, 2),
            "tilt": round(abs(math.sin(t * 0.6) * 3.8) + abs(math.cos(t * 0.5) * 2.8), 2),
        }
        foot_pressure = self._foot_pressure(t, gait)
        contact_ratio = sum(1 for item in foot_pressure.values() if item["contact"]) / 4.0
        terrain = self._terrain(t, risk)
        obstacle_distance = round(max(0.18, 2.2 - risk * 1.7 + math.sin(t * 0.3) * 0.1), 2)
        battery_voltage = round(max(10.6, 12.2 - t * 0.00015 - speed * 0.15), 2)
        battery_percent = round(max(8.0, min(100.0, (battery_voltage - 10.5) / 2.1 * 100.0)), 1)
        safety_faults = self._faults(battery_voltage, attitude, risk)
        camera_frame = self._svg_frame(t, terrain, obstacle_distance)
        self.state = RobotState(
            timestamp=now,
            uptime_s=round(t, 1),
            mode=mode,
            gait=gait,
            command=self.command,
            speed=round(speed, 2),
            battery_voltage=battery_voltage,
            battery_percent=battery_percent,
            logic_voltage=round(3.3 + math.sin(t * 0.5) * 0.02, 2),
            current_a=round(0.7 + speed * 2.4 + risk * 0.6, 2),
            power_w=round(battery_voltage * (0.7 + speed * 2.4 + risk * 0.6), 2),
            temperature_c=round(33.0 + speed * 8.0 + risk * 5.0, 1),
            humidity_percent=round(54.0 + math.sin(t / 15.0) * 3.0, 1),
            air_quality_eco2=int(445 + risk * 120 + math.sin(t / 18.0) * 20),
            object_temp_c=round(30.0 + risk * 6.0 + math.cos(t / 10.0) * 1.5, 1),
            gps={
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "alt_m": round(17.0 + math.sin(t / 30.0) * 1.2, 2),
                "fix": "3D",
                "satellites": 9 + int(abs(math.sin(t / 20.0)) * 3),
                "speed_mps": round(speed, 2),
                "heading_deg": round((t * 4.0) % 360.0, 2),
            },
            imu={"sample_hz": 500, "status": "ok", "temperature_c": round(32.0 + risk * 4.0, 1)},
            accelerometer=accel,
            gyroscope=gyro,
            magnetometer={
                "x": round(24.0 + math.sin(t / 8.0) * 2.0, 2),
                "y": round(-12.0 + math.cos(t / 7.0) * 2.0, 2),
                "z": round(41.0 + math.sin(t / 9.0) * 1.5, 2),
                "unit": "uT",
            },
            attitude=attitude,
            foot_pressure=foot_pressure,
            reflex={
                "enabled": self.command != "shutdown",
                "gain": round(0.35 + risk * 0.35, 2),
                "threshold_voltage": round(1.0 - risk * 0.22, 2),
                "last_trigger": self._last_reflex(foot_pressure),
                "contact_ratio": round(contact_ratio, 2),
                "loop_latency_us": round(1.3 + risk * 0.9, 2),
            },
            cpg={
                "frequency_hz": round(0.0 if gait == "stand" else 1.0 + speed * 1.6, 2),
                "phase": self._cpg_phase(t, gait),
                "amplitude": round(0.0 if gait == "stand" else 0.22 + speed * 0.25, 2),
            },
            vision={
                "terrain": terrain,
                "nearest_obstacle_m": obstacle_distance,
                "obstacle_count": int(risk * 5) + (1 if terrain != "flat" else 0),
                "optical_flow": {"x": round(math.sin(t) * 0.18, 3), "y": round(math.cos(t) * 0.12, 3), "magnitude": round(0.2 + risk, 3)},
                "confidence": round(0.92 - risk * 0.25, 2),
            },
            camera={
                "front": camera_frame,
                "depth": camera_frame,
                "status": "simulated",
                "fps": 24,
                "resolution": "640x360",
            },
            navigation={
                "pose": {"x": round(math.sin(t / 25.0) * 1.2, 2), "y": round(math.cos(t / 25.0) * 1.2, 2), "yaw": attitude["yaw"]},
                "target": {"x": 2.0, "y": 1.0},
                "distance_to_target_m": round(max(0.0, 2.2 - t * speed * 0.01), 2),
                "path_state": "tracking" if mode in {"locomotion", "exploration"} else "hold",
            },
            ai={
                "policy": "disabled_classical_cpg_reflex",
                "terrain_class": terrain,
                "risk": round(risk, 2),
                "stability": round(1.0 - risk, 2),
                "decision": mode,
                "inference_ms": 0.0,
            },
            communication={
                "can": "ok",
                "i2c": "ok",
                "uart": "ok",
                "wifi": "ok",
                "packet_sequence": self.sequence,
                "last_packet_age_ms": 0,
            },
            safety={
                "state": "fault" if safety_faults else "safe",
                "faults": safety_faults,
                "estop": self.command == "shutdown",
                "watchdog": "ok",
            },
            actuators=self._actuators(t, gait, speed),
            logs=list(self.logs),
        )
        return asdict(self.state)

    def _mode_gait_speed(self):
        if self.command == "shutdown":
            return "shutdown", "stop", 0.0
        if self.command == "recover":
            return "recover", "crawl", 0.08
        if self.command == "explore":
            return "exploration", "walk", 0.2
        if self.command == "walk":
            return "locomotion", "trot", 0.35
        return "idle", "stand", 0.0

    def _risk(self, t):
        if self.command == "shutdown":
            return 1.0
        base = 0.12 + (0.18 if self.command in {"walk", "explore"} else 0.0)
        pulse = (math.sin(t / 8.0) + 1.0) * 0.18
        return max(0.0, min(0.95, base + pulse))

    def _terrain(self, t, risk):
        terrains = ["flat", "carpet", "gravel", "slope"]
        return terrains[int((t / 18.0 + risk * 2.0) % len(terrains))]

    def _foot_pressure(self, t, gait):
        phase_offsets = {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0}
        if gait == "walk":
            phase_offsets = {"FL": 0.0, "FR": 0.5, "RL": 0.75, "RR": 0.25}
        data = {}
        for leg in LEGS:
            phase = (t * 1.3 + phase_offsets[leg]) % 1.0
            contact = gait == "stand" or phase > 0.45
            pressure = 0.72 if gait == "stand" else max(0.05, math.sin(math.pi * phase))
            data[leg] = {
                "pressure": round(pressure, 2),
                "contact": bool(contact),
                "fsr_voltage": round(0.35 + pressure * 1.25, 2),
                "load_n": round(pressure * 22.0, 2),
            }
        return data

    def _last_reflex(self, foot_pressure):
        active = [leg for leg, value in foot_pressure.items() if value["pressure"] > 0.82]
        return active[0] if active else "none"

    def _cpg_phase(self, t, gait):
        if gait == "stand":
            return {leg: 0.0 for leg in LEGS}
        offsets = {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0}
        return {leg: round((t * 1.3 + offsets[leg]) % 1.0, 2) for leg in LEGS}

    def _faults(self, battery_voltage, attitude, risk):
        faults = []
        if battery_voltage <= 10.5:
            faults.append("battery_low")
        if attitude["tilt"] >= 45.0:
            faults.append("tilt")
        if risk >= 0.82:
            faults.append("high_risk")
        if self.command == "shutdown":
            faults.append("estop")
        return faults

    def _actuators(self, t, gait, speed):
        return build_locomotion_frame(t, gait, speed)

    def _svg_frame(self, t, terrain, obstacle_distance):
        width = 640
        height = 360
        horizon = 120 + math.sin(t / 4.0) * 8
        obstacle_x = 320 + math.sin(t / 5.0) * 160
        obstacle_size = max(24, 90 - obstacle_distance * 18)
        svg = f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\"><rect width=\"640\" height=\"360\" fill=\"#dbeafe\"/><rect y=\"{horizon}\" width=\"640\" height=\"{360-horizon}\" fill=\"#334155\"/><path d=\"M0 360 L250 {horizon} L390 {horizon} L640 360 Z\" fill=\"#475569\"/><circle cx=\"{obstacle_x:.1f}\" cy=\"{horizon+110:.1f}\" r=\"{obstacle_size:.1f}\" fill=\"#ef4444\"/><text x=\"24\" y=\"36\" font-family=\"Arial\" font-size=\"22\" fill=\"#0f172a\">Front camera</text><text x=\"24\" y=\"66\" font-family=\"Arial\" font-size=\"16\" fill=\"#334155\">Terrain: {terrain} | Obstacle: {obstacle_distance:.2f} m</text></svg>"
        return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def build_demo_packet():
    return TelemetryState().snapshot()
