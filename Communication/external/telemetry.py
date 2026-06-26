import json
import time


class Telemetry:
    def __init__(self):
        self.last = {}
        self.sequence = 0

    def encode(self, packet):
        self.sequence += 1
        payload = dict(packet)
        payload["timestamp"] = time.time()
        payload["sequence"] = self.sequence
        self.last = payload
        return json.dumps(payload, separators=(",", ":"))

    def decode(self, payload):
        data = json.loads(payload)
        self.last = data
        return data

    def merge(self, *packets):
        merged = {}
        for packet in packets:
            merged.update(packet or {})
        return merged
