def detect_obstacles(frame):
    try:
        import cv2
        import numpy as np
    except Exception:
        return []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    obstacles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 300:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        obstacles.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h), "area": float(area)})
    return sorted(obstacles, key=lambda item: item["area"], reverse=True)
