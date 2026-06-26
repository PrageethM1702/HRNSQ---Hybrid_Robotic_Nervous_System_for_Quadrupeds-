import asyncio
from watchdog import Watchdog
from fault_detection import FaultDetector
from safe_shutdown import build_shutdown_command

async def main_loop():
    watchdog = Watchdog(timeout=1.0)
    detector = FaultDetector()

    telemetry = {
        "battery_voltage": 12.0,
        "logic_voltage": 3.3,
        "temperature_c": 30.0,
        "tilt_deg": 0.0,
        "reflex_age_s": 0.0,
        "gpio_voltage": 3.3,
    }

    while True:
        watchdog.kick()
        faults = detector.evaluate(telemetry)
        if watchdog.expired():
            faults.append("watchdog_timeout")
        if faults:
            print("Detected faults:", faults)
            print(build_shutdown_command(",".join(faults)))
            break
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
