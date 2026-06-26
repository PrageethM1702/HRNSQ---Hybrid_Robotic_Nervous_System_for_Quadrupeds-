import math


def plan_waypoints(start, goal, steps=10):
    sx, sy = start
    gx, gy = goal
    return [
        (sx + (gx - sx) * i / steps, sy + (gy - sy) * i / steps)
        for i in range(steps + 1)
    ]


def track_waypoint(pose, waypoint):
    dx = waypoint[0] - pose.get("x", 0.0)
    dy = waypoint[1] - pose.get("y", 0.0)
    distance = math.hypot(dx, dy)
    heading = math.atan2(dy, dx)
    return {"distance": distance, "heading": heading, "speed": min(0.4, distance)}
