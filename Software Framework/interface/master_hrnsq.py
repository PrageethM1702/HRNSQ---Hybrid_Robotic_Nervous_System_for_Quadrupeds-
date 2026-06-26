import json
from telemetry_state import TelemetryState


class HRNSQMaster:
    def __init__(self):
        self.telemetry = TelemetryState()

    def update(self, telemetry):
        return self.telemetry.ingest(telemetry)

    def command(self, command):
        self.telemetry.set_command(command)
        return self.telemetry.snapshot()

    def packet(self):
        return json.dumps(self.telemetry.snapshot(), separators=(",", ":"))


if __name__ == "__main__":
    master = HRNSQMaster()
    print(master.packet())
