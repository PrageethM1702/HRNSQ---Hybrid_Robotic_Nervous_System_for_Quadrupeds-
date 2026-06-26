from obstacle_detector import detect_obstacles
from terrain_classifier import classify_terrain


class PerceptionNode:
    def process(self, frame):
        terrain = classify_terrain(frame)
        obstacles = detect_obstacles(frame)
        nearest = 1.0
        if obstacles:
            nearest = max(0.05, 1.0 - min(1.0, obstacles[0]["area"] / 50000.0))
        return {
            "terrain": terrain,
            "obstacles": obstacles[:8],
            "nearest_obstacle_m": round(nearest, 3),
        }
