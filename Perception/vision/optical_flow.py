class OpticalFlowTracker:
    def __init__(self):
        self.previous = None

    def update(self, frame):
        try:
            import cv2
            import numpy as np
        except Exception:
            return {"flow": (0.0, 0.0), "magnitude": 0.0}
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.previous is None:
            self.previous = gray
            return {"flow": (0.0, 0.0), "magnitude": 0.0}
        flow = cv2.calcOpticalFlowFarneback(self.previous, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        self.previous = gray
        mean = flow.reshape(-1, 2).mean(axis=0)
        magnitude = np.linalg.norm(flow, axis=2).mean()
        return {"flow": (float(mean[0]), float(mean[1])), "magnitude": float(magnitude)}
