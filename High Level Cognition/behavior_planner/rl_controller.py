class RLController:
    def command(self, state):
        risk = float(state.get("risk", 0.0))
        target = state.get("target", None)
        if risk > 0.7:
            return {"command": "recover", "speed": 0.05}
        if target:
            return {"command": "walk", "speed": min(0.45, float(state.get("target_speed", 0.25)))}
        return {"command": "stand", "speed": 0.0}
