class HRNSQPyBulletEnv:
    def __init__(self, render=False):
        self.render = render
        self.client = None
        self.robot = None

    def connect(self):
        try:
            import pybullet as p
            import pybullet_data
        except Exception as exc:
            raise RuntimeError("Install pybullet to run this environment") from exc
        self.client = p.connect(p.GUI if self.render else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        return self.client

    def reset(self):
        if self.client is None:
            self.connect()
        return {"position": (0.0, 0.0, 0.25), "velocity": 0.0}

    def step(self, action):
        speed = float(action.get("speed", 0.0))
        reward = speed - 0.05 * abs(float(action.get("turn", 0.0)))
        return {"velocity": speed}, reward, False, {}
