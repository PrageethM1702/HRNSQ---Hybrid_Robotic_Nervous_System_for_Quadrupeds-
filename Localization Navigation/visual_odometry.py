class VisualOdometry:
    def __init__(self, scale=0.001):
        self.scale = scale
        self.pose = {"x": 0.0, "y": 0.0, "yaw": 0.0}

    def update(self, flow):
        vx, vy = flow.get("flow", (0.0, 0.0))
        self.pose["x"] += vx * self.scale
        self.pose["y"] += vy * self.scale
        self.pose["yaw"] += (vx - vy) * self.scale * 0.1
        return dict(self.pose)
