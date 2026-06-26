from state_machine import DecisionStateMachine


class RLPolicy:
    def __init__(self):
        self.machine = DecisionStateMachine()

    def act(self, observation):
        state = self.machine.update(observation)
        action = self.machine.output()
        action["state"] = state
        action["reflex_enable"] = float(observation.get("risk", 0.0)) > 0.35
        return action
