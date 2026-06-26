class ReflexPolicy:
    def __init__(self):
        self.base_gain = 0.55

    def decide(self, fused_state):
        risk = float(fused_state.get("risk", 0.0))
        slip = float(fused_state.get("slip", 0.0))
        load = float(fused_state.get("load", 0.5))
        gain = self.base_gain + 0.35 * risk + 0.20 * slip
        if load > 0.8:
            reflex = "load_support"
        elif slip > 0.35:
            reflex = "slip_recovery"
        elif risk > 0.55:
            reflex = "withdrawal"
        else:
            reflex = "none"
        return {"reflex": reflex, "gain": round(max(0.0, min(1.0, gain)), 4)}
