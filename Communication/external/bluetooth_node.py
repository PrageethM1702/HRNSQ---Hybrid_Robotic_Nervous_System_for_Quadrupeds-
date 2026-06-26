class BluetoothNode:
    def __init__(self):
        self.connected = False
        self.outbox = []

    def connect(self, address=None):
        self.connected = True
        return {"connected": True, "address": address}

    def send(self, message):
        if not self.connected:
            raise RuntimeError("Bluetooth node is not connected")
        self.outbox.append(message)
        return len(self.outbox)
