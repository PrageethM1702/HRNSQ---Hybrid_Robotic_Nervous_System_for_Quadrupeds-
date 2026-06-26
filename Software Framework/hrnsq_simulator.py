import asyncio
from pathlib import Path
import json
import math
import random
import sys
import time
import argparse
import websockets


LOW_LEVEL_PYTHON = Path(__file__).resolve().parents[1] / "Low Level Control" / "python"
if LOW_LEVEL_PYTHON.exists() and str(LOW_LEVEL_PYTHON) not in sys.path:
    sys.path.insert(0, str(LOW_LEVEL_PYTHON))

from hrnsq_locomotion import build_locomotion_frame

HOST = "127.0.0.1"
PORT = 9001
TICK_HZ  = 10
TICK_SEC = 1.0 / TICK_HZ

class RobotState:
    def __init__(self, mode="walk"):
        self.t           = 0.0
        self.mode        = mode
        self.phase       = {"FL": 0.0, "FR": 0.5, "RL": 0.5, "RR": 0.0}
        self.pose        = {"x": 0.0, "y": 0.0}
        self.target      = {"x": 10.0, "y": 5.0}
        self.log_buffer  = []
        self.packet_seq  = 0
        self.boot_time   = time.time()
        self.battery_cap = 100.0
        self.last_reflex = "none"
        self.reflex_timer = 0.0

    def uptime(self):
        return time.time() - self.boot_time

    def add_log(self, level, msg):
        ts = f"{self.uptime():.1f}s"
        self.log_buffer.append({"time": ts, "level": level, "message": msg})
        if len(self.log_buffer) > 30:
            self.log_buffer.pop(0)

def noise(scale=1.0):
    return random.gauss(0, scale)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def sin_wave(t, freq=1.0, amp=1.0, phase=0.0):
    return amp * math.sin(2 * math.pi * freq * t + phase)


def build_gps(t):
    lat = 6.8535 + (t * 0.000002) + noise(0.000001)
    lon = 79.9220 + noise(0.000001)
    return {
        "fix":         "3D",
        "lat":         round(lat, 7),
        "lon":         round(lon, 7),
        "alt_m":       round(20.0 + noise(0.1), 2),
        "satellites":  random.randint(9, 12),
        "heading_deg": round(5.0 + noise(1.5), 1),
        "speed_mps":   round(0.6 + noise(0.05), 3),
    }


def build_accelerometer(t, mode):
    if mode == "stand":
        ax = noise(0.05)
        ay = noise(0.05)
        az = 9.81 + noise(0.03)
    else:
        f = 2.0
        ax = sin_wave(t, f, 1.8) + noise(0.2)
        ay = sin_wave(t, f, 0.9, math.pi / 4) + noise(0.15)
        az = 9.81 + sin_wave(t, f * 2, 1.2) + noise(0.1)
    return {"x": round(ax, 4), "y": round(ay, 4), "z": round(az, 4)}


def build_gyroscope(t, mode):
    if mode == "stand":
        return {"x": round(noise(0.005), 4),
                "y": round(noise(0.005), 4),
                "z": round(noise(0.003), 4)}
    f = 2.0
    return {
        "x": round(sin_wave(t, f, 0.28) + noise(0.02), 4),
        "y": round(sin_wave(t, f, 0.18, 0.5) + noise(0.02), 4),
        "z": round(noise(0.03), 4),
    }


def build_attitude(t, mode):
    if mode == "stand":
        roll  = noise(0.2)
        pitch = noise(0.2)
        yaw   = 5.0 + noise(0.1)
    else:
        f     = 2.0
        roll  = sin_wave(t, f, 2.8) + noise(0.2)
        pitch = sin_wave(t, f, 1.5, 0.8) + noise(0.2)
        yaw   = 5.0 + sin_wave(t, 0.05, 0.3) + noise(0.05)
    tilt = math.sqrt(roll ** 2 + pitch ** 2)
    return {
        "roll":  round(roll, 2),
        "pitch": round(pitch, 2),
        "yaw":   round(yaw, 2),
        "tilt":  round(tilt, 2),
    }


def build_foot_pressure(t, mode, state):
    legs = ["FL", "FR", "RL", "RR"]
    feet = {}
    f    = 2.0 if mode != "stand" else 0.0
    for leg in legs:
        ph = state.phase[leg]
        if mode == "stand":
            raw = clamp(0.55 + noise(0.02), 0.0, 1.0)
        else:
            cycle = math.sin(2 * math.pi * f * t + ph * 2 * math.pi)
            raw   = clamp(0.5 + 0.45 * cycle + noise(0.03), 0.0, 1.0)

        if mode != "stand" and random.random() < 0.003:
            state.last_reflex  = f"{leg}_slip@{t:.1f}s"
            state.reflex_timer = t

        feet[leg] = {
            "pressure":    round(raw, 3),
            "contact":     raw > 0.2,
            "fsr_voltage": round(raw * 3.3, 3),
            "load_n":      round(raw * 120 + noise(1.5), 1),
        }
    return feet


def build_cpg(t, mode):
    if mode == "stand":
        return {"frequency_hz": 0.0,
                "phase": {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0}}
    base = (t * 2.0) % 1.0
    return {
        "frequency_hz": 2.0,
        "phase": {
            "FL": round(base, 3),
            "FR": round((base + 0.5) % 1.0, 3),
            "RL": round((base + 0.5) % 1.0, 3),
            "RR": round(base, 3),
        },
    }


def build_vision(t):
    terrains  = ["grass", "pavement", "gravel", "dirt"]
    terrain   = random.choices(terrains, weights=[40, 35, 15, 10])[0]
    obs_count = random.choices([0, 1, 2, 3], weights=[60, 25, 12, 3])[0]
    nearest   = round(random.uniform(0.8, 4.5), 2) if obs_count > 0 else None
    return {
        "terrain":            terrain,
        "confidence":         round(random.uniform(0.87, 0.97), 3),
        "obstacle_count":     obs_count,
        "nearest_obstacle_m": nearest,
        "optical_flow": {
            "x": round(sin_wave(t, 2.0, 0.04) + noise(0.005), 4),
            "y": round(sin_wave(t, 2.0, 0.015, 0.3) + noise(0.003), 4),
        },
    }


def build_navigation(t, state, mode):
    speed = {"walk": 0.6, "explore": 0.4, "stand": 0.0, "recover": 0.2}.get(mode, 0.0)
    state.pose["x"] = round(state.pose["x"] + speed * TICK_SEC * math.cos(math.radians(5.0)), 3)
    state.pose["y"] = round(state.pose["y"] + speed * TICK_SEC * math.sin(math.radians(5.0)), 3)
    dx   = state.target["x"] - state.pose["x"]
    dy   = state.target["y"] - state.pose["y"]
    dist = round(math.sqrt(dx * dx + dy * dy), 2)
    return {
        "path_state":           "navigating" if dist > 0.5 else "arrived",
        "pose":                 {"x": state.pose["x"], "y": state.pose["y"]},
        "target":               state.target,
        "distance_to_target_m": dist,
    }


def build_power(t, mode, state):
    drain = {"stand": 0.008, "walk": 0.025, "explore": 0.030, "recover": 0.015}.get(mode, 0.02)
    state.battery_cap = max(5.0, state.battery_cap - drain * TICK_SEC)
    pct     = state.battery_cap
    voltage = 12.0 + (pct / 100.0) * 4.8 + noise(0.02)
    power_w = {"stand": 35, "walk": 105, "explore": 118, "recover": 55}.get(mode, 80) + noise(3)
    return {
        "battery_percent": round(pct, 1),
        "battery_voltage": round(voltage, 2),
        "current_a":       round(power_w / voltage, 2),
        "power_w":         round(power_w, 1),
        "logic_voltage":   round(5.0 + noise(0.01), 3),
    }


def build_environment(t):
    return {
        "temperature_c":    round(29.5 + sin_wave(t, 1 / 3600, 2.0) + noise(0.1), 1),
        "object_temp_c":    round(32.0 + noise(0.5), 1),
        "humidity_percent": round(72.0 + sin_wave(t, 1 / 1800, 5.0) + noise(0.5), 1),
        "air_quality_eco2": random.randint(415, 445),
    }


def build_ai(t, mode, vision):
    w        = [20, 20, 20, 40] if vision["obstacle_count"] > 0 else [70, 15, 10, 5]
    decision = random.choices(["continue", "adjust_gait", "slow_down", "obstacle_avoid"], weights=w)[0]
    risk     = round(clamp(0.08 + vision["obstacle_count"] * 0.07 + noise(0.01), 0.0, 1.0), 3)
    return {
        "policy":        "disabled_classical_cpg_reflex",
        "decision":      decision,
        "stability":     round(clamp(0.92 - abs(sin_wave(t, 0.3, 0.04)), 0.7, 0.99), 3),
        "risk":          risk,
        "inference_ms":  0.0,
        "terrain_class": vision["terrain"],
    }


def build_communication(state):
    state.packet_seq += 1
    return {
        "packet_sequence": state.packet_seq,
        "can":  "1Mbit/s",
        "i2c":  "400kHz",
        "uart": "115200",
        "wifi": "-62dBm",
    }


def build_actuators(t, mode):
    gait = "stand" if mode == "stand" else "trot"
    speed = {"walk": 0.35, "explore": 0.2, "recover": 0.08, "stand": 0.0}.get(mode, 0.0)
    return build_locomotion_frame(t, gait, speed)


def build_logs(state, ai, vision):
    t = state.t
    if int(t * 10) % 30 == 0:
        state.add_log("INFO", f"Gait cycle OK | CPG 2.00 Hz | stability {ai['stability']:.2f}")
    if int(t * 10) % 50 == 0:
        state.add_log("INFO", f"Battery {state.battery_cap:.1f}% | {ai['inference_ms']}ms inference")
    if vision["obstacle_count"] > 1 and int(t * 10) % 20 == 0:
        state.add_log("WARN", f"Obstacle at {vision.get('nearest_obstacle_m','?')}m — avoidance active")
    if state.last_reflex != "none" and abs(t - state.reflex_timer) < 0.5:
        state.add_log("WARN", f"Reflex triggered: {state.last_reflex}")
    if int(t * 10) % 100 == 0:
        state.add_log("INFO", f"GPS fix 3D | pose {state.pose['x']:.1f},{state.pose['y']:.1f} m")
    if state.battery_cap < 20 and int(t * 10) % 40 == 0:
        state.add_log("WARN", f"LOW BATTERY: {state.battery_cap:.1f}%")
    return state.log_buffer

def build_frame(state):
    t      = state.t
    mode   = state.mode
    accel  = build_accelerometer(t, mode)
    gyro   = build_gyroscope(t, mode)
    att    = build_attitude(t, mode)
    gps    = build_gps(t)
    feet   = build_foot_pressure(t, mode, state)
    cpg    = build_cpg(t, mode)
    vision = build_vision(t)
    nav    = build_navigation(t, state, mode)
    power  = build_power(t, mode, state)
    env    = build_environment(t)
    ai     = build_ai(t, mode, vision)
    comms  = build_communication(state)
    acts   = build_actuators(t, mode)
    logs   = build_logs(state, ai, vision)
    speed  = round(0.6 + noise(0.04), 3) if mode in ("walk", "explore") else 0.0

    return {
        "timestamp":   time.time(),
        "mode":        mode,
        "gait":        "trot" if mode == "walk" else ("stand" if mode == "stand" else mode),
        "speed":       speed,
        "safety":      {"state": "safe" if ai["risk"] < 0.6 else "caution"},

        "accelerometer": accel,
        "gyroscope":     gyro,
        "attitude":      att,
        "imu":           {"status": "ok"},

        "gps":        gps,
        "navigation": nav,

        "foot_pressure": feet,
        "reflex": {
            "last_trigger":      state.last_reflex,
            "gain":              1.4,
            "threshold_voltage": 0.45,
            "contact_ratio":     round(sum(1 for f in feet.values() if f["contact"]) / 4, 2),
            "loop_latency_us":   round(random.uniform(180, 280), 1),
        },

        "cpg":    cpg,
        "vision": vision,
        "ai":     ai,

        "battery_percent": power["battery_percent"],
        "battery_voltage": power["battery_voltage"],
        "current_a":       power["current_a"],
        "power_w":         power["power_w"],
        "logic_voltage":   power["logic_voltage"],

        "temperature_c":    env["temperature_c"],
        "object_temp_c":    env["object_temp_c"],
        "humidity_percent": env["humidity_percent"],
        "air_quality_eco2": env["air_quality_eco2"],

        "communication": comms,
        "actuators":     acts,

        "camera": {
            "status":     "online",
            "resolution": "640x480",
            "fps":        30,
            "front":      "",
            "depth":      "",
        },

        "logs": logs,
    }

async def handler(websocket, mode_ref):
    state = RobotState(mode_ref[0])
    state.add_log("INFO", "HRNS-Q boot complete — telemetry online")
    state.add_log("INFO", f"Initial mode: {mode_ref[0]}")
    print(f"[HRNS-Q] Client connected: {websocket.remote_address}")

    async def recv_commands():
        async for raw in websocket:
            try:
                cmd = json.loads(raw).get("command", "")
                if cmd in ("stand", "walk", "explore", "recover", "shutdown"):
                    state.mode  = "stand" if cmd == "shutdown" else cmd
                    mode_ref[0] = state.mode
                    state.add_log("INFO", f"Command received: {cmd.upper()}")
                    print(f"[HRNS-Q] Command: {cmd}")
            except Exception as e:
                print(f"[HRNS-Q] Bad command: {e}")

    asyncio.ensure_future(recv_commands())

    try:
        while True:
            state.t += TICK_SEC
            frame    = build_frame(state)
            await websocket.send(json.dumps(frame))
            await asyncio.sleep(TICK_SEC)
    except websockets.exceptions.ConnectionClosed:
        print(f"[HRNS-Q] Client disconnected: {websocket.remote_address}")

async def main(port, mode):
    mode_ref = [mode]
    print("╔══════════════════════════════════════════╗")
    print("║    HRNS-Q Telemetry Simulator v1.1       ║")
    print("╠══════════════════════════════════════════╣")
    print(f"║  WebSocket : ws://127.0.0.1:{port}          ║")
    print(f"║  Mode      : {mode:<28}║")
    print("║  Rate      : 10 Hz                       ║")
    print("╚══════════════════════════════════════════╝")
    print()
    print("  Step 1: Keep this terminal running.")
    print("  Step 2: Open a 2nd terminal and run:")
    print(f'          python -m http.server 5500 --bind 127.0.0.1')
    print(f'          (run from the dashboard root folder)')
    print("  Step 3: Open browser -> http://127.0.0.1:5500/templates/dashboard.html")
    print()

    stop = asyncio.Event()
    async with websockets.serve(
        lambda ws: handler(ws, mode_ref),
        HOST, port,
        origins=None
    ):
        try:
            await stop.wait()
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HRNS-Q telemetry simulator")
    parser.add_argument("--mode", default="walk",
                        choices=["stand", "walk", "explore", "recover"])
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.port, args.mode))
    except KeyboardInterrupt:
        print("\n[HRNS-Q] Simulator stopped.")
