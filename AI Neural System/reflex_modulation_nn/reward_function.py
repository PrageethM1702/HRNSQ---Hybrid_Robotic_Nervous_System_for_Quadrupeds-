def reflex_reward(state, action):
    stability = float(state.get("stability", 0.0))
    clearance = float(state.get("foot_clearance", 0.0))
    slip = float(state.get("slip", 0.0))
    energy = float(action.get("gain", 0.0)) ** 2
    return stability + 0.4 * clearance - 0.8 * slip - 0.05 * energy
