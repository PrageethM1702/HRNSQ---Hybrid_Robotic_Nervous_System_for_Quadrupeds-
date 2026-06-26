from model import GaitModel
from sim_env import HRNSQSimEnv


def train(episodes=10, steps=300):
    env = HRNSQSimEnv()
    best = {"gait": "trot", "reward": -10**9}
    for gait in ("walk", "trot", "pace", "bound"):
        model = GaitModel(gait=gait)
        total = 0.0
        for _ in range(episodes):
            state = env.reset()
            for _ in range(steps):
                action = model.predict({"time": state["time"], "speed": 0.35, "terrain_gain": 1.0})
                state, reward, done, _ = env.step(action)
                total += reward
                if done:
                    break
        if total > best["reward"]:
            best = {"gait": gait, "reward": total}
    return best


if __name__ == "__main__":
    print(train())
