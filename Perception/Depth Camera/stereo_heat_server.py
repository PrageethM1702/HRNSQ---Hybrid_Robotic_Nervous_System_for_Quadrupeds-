from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import cv2
    import numpy as np
except Exception as exc:
    cv2 = None
    np = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


HOST = os.environ.get("HRNSQ_VISION_HOST", "0.0.0.0")
PORT = int(os.environ.get("HRNSQ_VISION_PORT", "9100"))
LEFT_URL = os.environ.get("HRNSQ_ESP32_LEFT_URL", "http://192.168.1.51:81/stream")
RIGHT_URL = os.environ.get("HRNSQ_ESP32_RIGHT_URL", "http://192.168.1.52:81/stream")
NIGHT_CAM_INDEX = int(os.environ.get("HRNSQ_NIGHT_CAM_INDEX", "0"))
BASELINE_CM = 15.0
CAMERA_HEIGHT_CM = 6.0


class SharedState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.night_jpeg = None
        self.depth_jpeg = None
        self.reaction = {
            "reaction": "idle_scan",
            "detected": False,
            "confidence": 0.0,
            "note": "vision service starting",
        }

    def set_night(self, jpeg: bytes, reaction: dict) -> None:
        with self.lock:
            self.night_jpeg = jpeg
            self.reaction = reaction

    def set_depth(self, jpeg: bytes) -> None:
        with self.lock:
            self.depth_jpeg = jpeg

    def get(self):
        with self.lock:
            return self.night_jpeg, self.depth_jpeg, dict(self.reaction)


STATE = SharedState()


def placeholder(text: str, width: int = 640, height: int = 360) -> bytes:
    if cv2 is None:
        return b""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (31, 41, 55)
    cv2.putText(frame, text, (28, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (229, 231, 235), 2)
    ok, encoded = cv2.imencode(".jpg", frame)
    return encoded.tobytes() if ok else b""


def encode(frame) -> bytes | None:
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    return encoded.tobytes() if ok else None


def open_capture(source):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def night_worker() -> None:
    if cv2 is None:
        STATE.set_night(b"", {"reaction": "vision_unavailable", "detected": False, "note": str(IMPORT_ERROR)})
        return

    face_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    body_path = Path(cv2.data.haarcascades) / "haarcascade_upperbody.xml"
    face = cv2.CascadeClassifier(str(face_path))
    body = cv2.CascadeClassifier(str(body_path))
    cap = open_capture(NIGHT_CAM_INDEX)

    while True:
        ok, frame = cap.read()
        if not ok:
            STATE.set_night(
                placeholder("Night camera not connected"),
                {"reaction": "idle_scan", "detected": False, "note": "night camera not connected"},
            )
            time.sleep(0.5)
            cap.release()
            cap = open_capture(NIGHT_CAM_INDEX)
            continue

        frame = cv2.resize(frame, (640, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
        bodies = body.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(80, 100))
        reaction = classify_reaction(frame, faces, bodies)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (40, 220, 80), 2)
        for (x, y, w, h) in bodies:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 160, 255), 2)
        cv2.putText(frame, reaction["reaction"], (18, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        jpeg = encode(frame)
        if jpeg:
            STATE.set_night(jpeg, reaction)
        time.sleep(0.03)


def classify_reaction(frame, faces, bodies) -> dict:
    height, width = frame.shape[:2]
    detections = list(faces) if len(faces) else list(bodies)
    if not detections:
        return {"reaction": "idle_scan", "detected": False, "confidence": 0.0, "note": "no human detected"}

    x, y, w, h = max(detections, key=lambda box: box[2] * box[3])
    center_x = x + w / 2
    center_y = y + h / 2
    area_ratio = (w * h) / float(width * height)

    if center_y < height * 0.38:
        reaction = "look_up"
    elif abs(center_x - width / 2) < width * 0.18 and area_ratio > 0.08:
        reaction = "give_hand"
    else:
        reaction = "look_at_human"

    return {
        "reaction": reaction,
        "detected": True,
        "confidence": round(min(0.95, 0.45 + area_ratio * 4.0), 2),
        "center_x": round(center_x / width, 3),
        "center_y": round(center_y / height, 3),
        "note": f"baseline {BASELINE_CM}cm, camera height {CAMERA_HEIGHT_CM}cm",
    }


def depth_worker() -> None:
    if cv2 is None:
        return

    left = open_capture(LEFT_URL)
    right = open_capture(RIGHT_URL)
    while True:
        ok_l, frame_l = left.read()
        ok_r, frame_r = right.read()
        if not ok_l or not ok_r:
            STATE.set_depth(placeholder("ESP32 stereo streams not connected"))
            time.sleep(0.5)
            left.release()
            right.release()
            left = open_capture(LEFT_URL)
            right = open_capture(RIGHT_URL)
            continue

        heat = build_depth_heat(frame_l, frame_r)
        jpeg = encode(heat)
        if jpeg:
            STATE.set_depth(jpeg)
        time.sleep(0.05)


def build_depth_heat(left, right):
    left = cv2.resize(left, (320, 240))
    right = cv2.resize(right, (320, 240))
    gray_l = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    gray_r = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

    try:
        stereo = cv2.StereoBM_create(numDisparities=16 * 4, blockSize=15)
        disparity = stereo.compute(gray_l, gray_r).astype(np.float32)
        disparity = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
        disparity = np.uint8(disparity)
    except Exception:
        disparity = cv2.absdiff(gray_l, gray_r)

    heat = cv2.applyColorMap(disparity, cv2.COLORMAP_JET)
    cv2.putText(heat, "Stereo heat view (demo)", (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(heat, "baseline 15cm | height 6cm", (10, 222), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return cv2.resize(heat, (640, 360))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/reaction.json":
            _night, _depth, reaction = STATE.get()
            self._send_json(reaction)
            return
        if self.path == "/night.mjpg":
            self._stream("night")
            return
        if self.path == "/depth_heat.mjpg":
            self._stream("depth")
            return
        self._send_json({
            "service": "HRNS-Q vision",
            "night": "/night.mjpg",
            "depth_heat": "/depth_heat.mjpg",
            "reaction": "/reaction.json",
        })

    def _send_json(self, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _stream(self, stream_name):
        self.send_response(200)
        self.send_header("Age", "0")
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()
        while True:
            night, depth, _reaction = STATE.get()
            frame = night if stream_name == "night" else depth
            if not frame:
                frame = placeholder("Waiting for stream")
            try:
                self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
                time.sleep(0.08)
            except Exception:
                break

    def log_message(self, _format, *_args):
        return


def main() -> None:
    threading.Thread(target=night_worker, daemon=True).start()
    threading.Thread(target=depth_worker, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"HRNS-Q vision service: http://{HOST}:{PORT}")
    print(f"left ESP32: {LEFT_URL}")
    print(f"right ESP32: {RIGHT_URL}")
    server.serve_forever()


if __name__ == "__main__":
    main()
