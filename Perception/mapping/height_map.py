class HeightMap:
    def __init__(self):
        self.points = {}

    def add(self, x, y, z):
        self.points[(round(x, 2), round(y, 2))] = float(z)

    def slope_at(self, x, y):
        center = self.points.get((round(x, 2), round(y, 2)), 0.0)
        nearby = [z for (px, py), z in self.points.items() if abs(px - x) <= 0.2 and abs(py - y) <= 0.2]
        if not nearby:
            return 0.0
        return max(abs(z - center) for z in nearby)
