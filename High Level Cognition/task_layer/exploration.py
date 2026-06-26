def frontier_targets(local_map, limit=5):
    targets = []
    for cell in local_map.get("cells", []):
        if cell.get("state") == "frontier":
            targets.append((cell.get("x", 0), cell.get("y", 0)))
    return targets[:limit]


def choose_target(local_map, pose):
    targets = frontier_targets(local_map)
    if not targets:
        return None
    px = pose.get("x", 0.0)
    py = pose.get("y", 0.0)
    return min(targets, key=lambda t: (t[0] - px) ** 2 + (t[1] - py) ** 2)
