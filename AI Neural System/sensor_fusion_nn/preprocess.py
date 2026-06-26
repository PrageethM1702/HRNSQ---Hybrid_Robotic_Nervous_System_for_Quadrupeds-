def normalize_sensor_packet(packet):
    imu = packet.get("imu", {})
    pressure = packet.get("pressure", {})
    vision = packet.get("vision", {})
    power = packet.get("power", {})
    contacts = [float(v) > 0.2 for v in pressure.values()]
    return {
        "roll": float(imu.get("roll", 0.0)),
        "pitch": float(imu.get("pitch", 0.0)),
        "yaw_rate": float(imu.get("yaw_rate", 0.0)),
        "foot_contact_ratio": sum(contacts) / max(len(contacts), 1),
        "obstacle_distance_risk": max(0.0, min(1.0, 1.0 - float(vision.get("nearest_obstacle_m", 1.0)))),
        "motor_temp": float(packet.get("motor_temp", 35.0)),
        "battery_voltage": float(power.get("voltage", 12.0)),
    }


def batch_normalize(packets):
    return [normalize_sensor_packet(packet) for packet in packets]
