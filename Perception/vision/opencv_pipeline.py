def process_frame(frame):
    try:
        import cv2
    except Exception:
        return {"frame": frame, "edges": None, "gray": None}
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 140)
    return {"frame": frame, "gray": gray, "edges": edges}
