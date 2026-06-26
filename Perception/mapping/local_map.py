class LocalMap:
    def __init__(self, resolution=0.1):
        self.resolution = resolution
        self.cells = {}

    def key(self, x, y):
        return (round(x / self.resolution), round(y / self.resolution))

    def update_obstacle(self, x, y, occupied=True):
        self.cells[self.key(x, y)] = {"occupied": occupied, "x": x, "y": y}

    def nearest_obstacles(self, x, y, radius=1.0):
        out = []
        for cell in self.cells.values():
            dx = cell["x"] - x
            dy = cell["y"] - y
            if cell["occupied"] and dx * dx + dy * dy <= radius * radius:
                out.append(cell)
        return out
