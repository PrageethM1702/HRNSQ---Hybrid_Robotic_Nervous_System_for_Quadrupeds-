import torch
from ultralytics import YOLO


class ObstacleDetector:
    def __init__(self, model_path="yolov8n.pt", device=None, conf_threshold=0.3):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            device=self.device,
            conf=self.conf_threshold,
            verbose=False
        )

        detections = []

        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })

        return detections
