import socket


class WifiNode:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port

    def send_udp(self, target_host, payload):
        data = payload.encode() if isinstance(payload, str) else payload
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return sock.sendto(data, (target_host, self.port))
        finally:
            sock.close()
