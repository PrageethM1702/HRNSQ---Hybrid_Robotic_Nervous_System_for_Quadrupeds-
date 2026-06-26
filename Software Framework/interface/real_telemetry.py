from __future__ import annotations

import base64
import math
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path
from urllib.request import urlopen

from telemetry_state import LEGS, RobotState


LOW_LEVEL_PYTHON = Path(__file__).resolve().parents[2] / "Low Level Control" / "python"
if LOW_LEVEL_PYTHON.exists() and str(LOW_LEVEL_PYTHON) not in sys.path:
    sys.path.insert(0, str(LOW_LEVEL_PYTHON))

from hrnsq_locomotion import build_locomotion_frame


class RealTelemetryState:
    def __init__(self):
        self.started = time.time()
        self.sequence = 0
        self.command = "stand"
        self.logs = []
        self._hardware = None
        self._hardware_error = None
        self._servo_output = None
        self.vision_base_url = os.environ.get("HRNSQ_VISION_URL", "http://127.0.0.1:9100")

    def set_command(self, command):
        if command in {"stand", "walk", "explore", "recover", "shutdown"}:
            self.command = command
            self.add_log("command", command)

    def ingest(self, packet):
        if "command" in packet:
            self.set_command(str(packet["command"]))
        return self.snapshot()

    def add_log(self, level, message):
        self.logs.append({"time": time.strftime("%H:%M:%S"), "level": level, "message": message})
        self.logs = self.logs[-30:]

    def snapshot(self):
        self.sequence += 1
        now = time.time()
        uptime = now - self.started
        mode, gait, speed = self._mode_gait_speed()
        sensors = self._read_sensors()
        reaction = self._read_reaction()
        actuators = build_locomotion_frame(uptime, gait, speed)
        self._apply_servos(actuators)

        faults = []
        if self._hardware_error:
            faults.append("hardware_read_unavailable")
        if self.command == "shutdown":
            faults.append("estop")

        state = RobotState(
            timestamp=now,
            mode=mode,
            gait=gait,
            command=self.command,
            speed=speed,
            uptime_s=round(uptime, 1),
            battery_voltage=sensors.get("battery_voltage", 0.0),
            battery_percent=sensors.get("battery_percent", 0.0),
            logic_voltage=sensors.get("logic_voltage", 3.3),
            current_a=sensors.get("current_a", 0.0),
            power_w=sensors.get("power_w", 0.0),
            temperature_c=sensors.get("temperature_c", 0.0),
            humidity_percent=sensors.get("humidity_percent", 0.0),
            air_quality_eco2=sensors.get("air_quality_eco2", 0),
            object_temp_c=sensors.get("object_temp_c", 0.0),
            gps=sensors.get("gps", {"fix": "no module", "lat": None, "lon": None, "satellites": 0}),
            imu=sensors.get("imu", {"status": "unavailable"}),
            accelerometer=sensors.get("accelerometer", {"x": 0.0, "y": 0.0, "z": 0.0, "unit": "m/s2"}),
            gyroscope=sensors.get("gyroscope", {"x": 0.0, "y": 0.0, "z": 0.0, "unit": "deg/s"}),
            magnetometer=sensors.get("magnetometer", {}),
            attitude=sensors.get("attitude", {"roll": 0.0, "pitch": 0.0, "yaw": 0.0, "tilt": 0.0}),
            foot_pressure=sensors.get("foot_pressure", self._empty_feet()),
            reflex=sensors.get("reflex", self._reflex_from_feet(sensors.get("foot_pressure", self._empty_feet()))),
            cpg={
                "frequency_hz": 0.0 if gait == "stand" else round(1.0 + speed * 1.6, 2),
                "phase": self._cpg_phase(uptime, gait),
                "amplitude": 0.0 if gait == "stand" else 0.28,
            },
            vision=sensors.get("vision", {"terrain": reaction["reaction"], "confidence": reaction["confidence"], "obstacle_count": 1 if reaction["detected"] else 0, "nearest_obstacle_m": None, "optical_flow": {"x": 0, "y": 0}}),
            camera=sensors.get("camera", self._camera_streams()),
            navigation=sensors.get("navigation", {"path_state": "manual", "pose": {"x": 0, "y": 0}, "target": {"x": 0, "y": 0}}),
            ai={"policy": "opencv_human_reaction", "decision": reaction["reaction"], "risk": 0.2 if not faults else 0.7, "stability": 0.8 if not faults else 0.3, "inference_ms": 0.0, "terrain_class": "human" if reaction["detected"] else "none"},
            communication={"can": "optional", "i2c": sensors.get("i2c_status", "unknown"), "uart": sensors.get("uart_status", "unknown"), "wifi": "pi", "packet_sequence": self.sequence},
            safety={"state": "safe" if not faults else "caution", "faults": faults, "estop": self.command == "shutdown", "watchdog": "host"},
            actuators=actuators,
            logs=list(self.logs),
        )
        return asdict(state)

    def _read_sensors(self):
        if self._hardware is None:
            self._hardware = self._init_hardware()
        if not self._hardware:
            return {"i2c_status": "unavailable", "uart_status": "unavailable"}

        data = {"i2c_status": "ok", "uart_status": "not configured"}
        try:
            if self._hardware.get("bmp280"):
                bmp = self._hardware["bmp280"]
                data["temperature_c"] = round(float(bmp.temperature), 1)
                data["gps"] = {"fix": "sensor only", "alt_m": round(float(bmp.altitude), 2), "satellites": 0}
            if self._hardware.get("si7021"):
                si = self._hardware["si7021"]
                data["humidity_percent"] = round(float(si.relative_humidity), 1)
                data.setdefault("temperature_c", round(float(si.temperature), 1))
            if self._hardware.get("mlx90614"):
                mlx = self._hardware["mlx90614"]
                data["object_temp_c"] = round(float(mlx.object_temperature), 1)
                data.setdefault("temperature_c", round(float(mlx.ambient_temperature), 1))
            if self._hardware.get("sgp30"):
                sgp = self._hardware["sgp30"]
                eco2, _tvoc = sgp.iaq_measure()
                data["air_quality_eco2"] = int(eco2)
            self._hardware_error = None
        except Exception as exc:
            self._hardware_error = str(exc)
            self.add_log("warn", f"hardware read failed: {exc}")
        return data

    def _init_hardware(self):
        try:
            import board
            import busio
        except Exception as exc:
            self._hardware_error = str(exc)
            self.add_log("warn", "real mode: Blinka/board libraries unavailable")
            return None

        hardware = {}
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            hardware["i2c"] = i2c
        except Exception as exc:
            self._hardware_error = str(exc)
            self.add_log("warn", f"real mode: I2C unavailable: {exc}")
            return None

        self._try_sensor(hardware, "bmp280", "adafruit_bmp280", "Adafruit_BMP280_I2C", address=0x77)
        self._try_sensor(hardware, "si7021", "adafruit_si7021", "SI7021")
        self._try_sensor(hardware, "mlx90614", "adafruit_mlx90614", "MLX90614")
        self._try_sensor(hardware, "sgp30", "adafruit_sgp30", "SGP30", address=0x58)
        return hardware

    def _try_sensor(self, hardware, key, module_name, class_name, address=None):
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            if address is None:
                hardware[key] = cls(hardware["i2c"])
            else:
                hardware[key] = cls(hardware["i2c"], address=address)
            self.add_log("info", f"{key} online")
        except Exception as exc:
            hardware[key] = None
            self.add_log("warn", f"{key} unavailable: {exc}")

    def _apply_servos(self, actuators):
        if os.environ.get("HRNSQ_ENABLE_SERVOS") != "1" or self.command == "shutdown":
            return
        try:
            if self._servo_output is None:
                from pca9685_servo_driver import PCA9685ServoOutput
                self._servo_output = PCA9685ServoOutput()
                self.add_log("info", "PCA9685 servo output enabled")
            self._servo_output.apply_frame(actuators)
        except Exception as exc:
            self.add_log("warn", f"servo output failed: {exc}")

    def _read_reaction(self):
        try:
            with urlopen(f"{self.vision_base_url}/reaction.json", timeout=0.15) as response:
                data = json.loads(response.read().decode("utf-8"))
            return {
                "reaction": data.get("reaction", "idle_scan"),
                "detected": bool(data.get("detected", False)),
                "confidence": float(data.get("confidence", 0.0)),
            }
        except Exception:
            return {"reaction": "vision_offline", "detected": False, "confidence": 0.0}

    def _mode_gait_speed(self):
        if self.command == "shutdown":
            return "shutdown", "stop", 0.0
        if self.command == "walk":
            return "real_locomotion", "trot", 0.25
        if self.command == "explore":
            return "real_explore", "walk", 0.15
        if self.command == "recover":
            return "real_recover", "crawl", 0.08
        return "real_idle", "stand", 0.0

    def _empty_feet(self):
        return {leg: {"pressure": 0.0, "contact": False, "fsr_voltage": 0.0, "load_n": 0.0} for leg in LEGS}

    def _reflex_from_feet(self, feet):
        contact_ratio = sum(1 for item in feet.values() if item.get("contact")) / 4.0
        return {"enabled": True, "gain": 0.0, "threshold_voltage": 0.0, "last_trigger": "none", "contact_ratio": round(contact_ratio, 2), "loop_latency_us": 0.0}

    def _cpg_phase(self, t, gait):
        if gait == "stand":
            return {leg: 0.0 for leg in LEGS}
        offsets = {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0}
        return {leg: round((t * 1.2 + offsets[leg]) % 1.0, 2) for leg in LEGS}

    def _camera_streams(self):
        return {
            "front": f"{self.vision_base_url}/night.mjpg",
            "depth": f"{self.vision_base_url}/depth_heat.mjpg",
            "status": "vision service",
            "fps": 12,
            "resolution": "640x360",
        }
