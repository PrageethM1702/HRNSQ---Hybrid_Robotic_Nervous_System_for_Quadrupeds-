import asyncio
import base64
import hashlib
import json
import struct

from telemetry_state import TelemetryState
from real_telemetry import RealTelemetryState


GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketClient:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, data):
        payload = data.encode("utf-8")
        length = len(payload)
        if length < 126:
            header = bytes([0x81, length])
        elif length < 65536:
            header = bytes([0x81, 126]) + struct.pack("!H", length)
        else:
            header = bytes([0x81, 127]) + struct.pack("!Q", length)
        self.writer.write(header + payload)
        await self.writer.drain()

    async def recv(self):
        head = await self.reader.readexactly(2)
        opcode = head[0] & 0x0F
        masked = head[1] & 0x80
        length = head[1] & 0x7F
        if length == 126:
            length = struct.unpack("!H", await self.reader.readexactly(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", await self.reader.readexactly(8))[0]
        mask = await self.reader.readexactly(4) if masked else b"\x00\x00\x00\x00"
        payload = await self.reader.readexactly(length) if length else b""
        data = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        if opcode == 8:
            raise ConnectionError("closed")
        return data.decode("utf-8")

    def close(self):
        self.writer.close()


class DashboardServer:
    def __init__(self):
        self.clients = set()
        self.source = "sim"
        self.sources = {"sim": TelemetryState(), "real": RealTelemetryState()}

    @property
    def telemetry(self):
        return self.sources[self.source]

    async def handle(self, reader, writer):
        client = None
        try:
            headers = await self._handshake(reader, writer)
            if not headers:
                writer.close()
                return
            client = WebSocketClient(reader, writer)
            self.clients.add(client)
            data = self.telemetry.snapshot()
            data["source"] = self.source
            await client.send(json.dumps(data))
            while True:
                message = await client.recv()
                packet = json.loads(message)
                if packet.get("source") in self.sources:
                    self.source = packet["source"]
                self.telemetry.ingest(packet)
                await self.broadcast()
        except Exception:
            pass
        finally:
            if client:
                self.clients.discard(client)
            writer.close()

    async def _handshake(self, reader, writer):
        request = await reader.readuntil(b"\r\n\r\n")
        lines = request.decode("utf-8", "ignore").split("\r\n")
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        key = headers.get("sec-websocket-key")
        if not key:
            return None
        accept = base64.b64encode(hashlib.sha1((key + GUID).encode("ascii")).digest()).decode("ascii")
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        )
        writer.write(response.encode("ascii"))
        await writer.drain()
        return headers

    async def broadcast(self):
        if not self.clients:
            return
        data = self.telemetry.snapshot()
        data["source"] = self.source
        payload = json.dumps(data)
        dead = []
        for client in list(self.clients):
            try:
                await client.send(payload)
            except Exception:
                dead.append(client)
        for client in dead:
            self.clients.discard(client)

    async def loop(self):
        while True:
            await self.broadcast()
            await asyncio.sleep(0.1)


async def main(host="0.0.0.0", port=9001):
    server = DashboardServer()
    socket_server = await asyncio.start_server(server.handle, host, port)
    async with socket_server:
        await server.loop()


if __name__ == "__main__":
    asyncio.run(main())
