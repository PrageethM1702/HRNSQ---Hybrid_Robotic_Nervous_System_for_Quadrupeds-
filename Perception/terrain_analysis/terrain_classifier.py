def classify(features):
    roughness = float(features.get("roughness", 0.0))
    slope = abs(float(features.get("slope", 0.0)))
    color = features.get("color", "unknown")
    if slope > 0.45:
        return {"terrain": "steep", "speed_limit": 0.08}
    if roughness > 0.7:
        return {"terrain": "rough", "speed_limit": 0.15}
    if color in ("green", "brown"):
        return {"terrain": "soft", "speed_limit": 0.22}
    return {"terrain": "flat", "speed_limit": 0.4}
