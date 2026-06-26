class HRNSQIsaacGymEnv:
    def __init__(self, num_envs=64):
        self.num_envs = num_envs
        self.step_count = 0

    def reset(self):
        self.step_count = 0
        return [{"roll": 0.0, "pitch": 0.0, "speed": 0.0} for _ in range(self.num_envs)]

    def step(self, actions):
        self.step_count += 1
        observations = []
        rewards = []
        done = []
        for action in actions:
            speed = float(action.get("speed", 0.0))
            observations.append({"roll": 0.0, "pitch": 0.0, "speed": speed})
            rewards.append(speed)
            done.append(self.step_count > 1000)
        return observations, rewards, done, {}
