def classify_terrain(frame):
    try:
        import cv2
        import numpy as np
    except Exception:
        return {"terrain": "unknown", "confidence": 0.0}
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2].mean()
    saturation = hsv[:, :, 1].mean()
    texture = cv2.Laplacian(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    if texture > 500 and saturation > 55:
        terrain = "grass"
    elif texture > 650:
        terrain = "gravel"
    elif value < 65:
        terrain = "dark"
    else:
        terrain = "flat"
    confidence = min(0.95, 0.45 + texture / 2500.0)
    return {"terrain": terrain, "confidence": round(float(confidence), 4)}
