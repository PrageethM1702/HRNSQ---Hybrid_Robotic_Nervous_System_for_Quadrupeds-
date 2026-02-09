import time
import threading

class Watchdog:
    def __init__(self, timeout_s=1.0):
        self.timeout_s = timeout_s
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        self.alive = True

    def heartbeat(self):
        with self.lock:
            self.last_heartbeat = time.time()

    def check(self):
        with self.lock:
            if time.time() - self.last_heartbeat > self.timeout_s:
                self.alive = False
        return self.alive

    def start_monitor(self, callback):
        def monitor():
            while True:
                if not self.check():
                    callback()
                    break
                time.sleep(0.01)
        t = threading.Thread(target=monitor, daemon=True)
        t.start()
