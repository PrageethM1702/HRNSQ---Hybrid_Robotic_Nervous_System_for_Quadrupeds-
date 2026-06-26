import time


class Watchdog:
    def __init__(self, timeout=0.5):
        self.timeout = timeout
        self.last_kick = time.monotonic()

    def kick(self):
        self.last_kick = time.monotonic()

    def expired(self):
        return time.monotonic() - self.last_kick > self.timeout
