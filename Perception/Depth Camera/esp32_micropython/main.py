import gc
import socket
import time

import network

try:
    import camera
except ImportError:
    camera = None

import config


BOUNDARY = b"frame"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if getattr(config, "STATIC_IP", ""):
        wlan.ifconfig((config.STATIC_IP, config.NETMASK, config.GATEWAY, config.DNS))
    if not wlan.isconnected():
        print("wifi connecting:", config.WIFI_SSID)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        for _ in range(40):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    if not wlan.isconnected():
        raise RuntimeError("Wi-Fi connection failed")
    print("wifi:", wlan.ifconfig())
    return wlan


def init_camera():
    if camera is None:
        print("ERROR: this MicroPython firmware has no camera module")
        return False

    try:
        camera.deinit()
    except Exception:
        pass

    try:
        camera.init(0, format=camera.JPEG)
    except TypeError:
        camera.init()

    frame_size = getattr(camera, getattr(config, "FRAME_SIZE", "QVGA"), None)
    if frame_size is not None:
        camera.framesize(frame_size)
    if hasattr(camera, "quality"):
        camera.quality(config.JPEG_QUALITY)
    if hasattr(camera, "flip"):
        camera.flip(0)
    if hasattr(camera, "mirror"):
        camera.mirror(0)

    print("camera ready")
    return True


def write_response(client, status, content_type, body):
    client.send(("HTTP/1.1 %s\r\n" % status).encode())
    client.send(("Content-Type: %s\r\n" % content_type).encode())
    client.send(("Content-Length: %d\r\n" % len(body)).encode())
    client.send(b"Connection: close\r\n\r\n")
    client.send(body)


def handle_root(client, ip):
    body = """<!doctype html>
<html><head><title>HRNS-Q ESP32-CAM</title></head>
<body style="font-family:Arial">
<h1>{name}</h1>
<p>Stream: <a href="/stream">/stream</a></p>
<img src="/stream" style="max-width:100%">
<p>URL: http://{ip}:{port}/stream</p>
</body></html>""".format(name=config.DEVICE_NAME, ip=ip, port=config.STREAM_PORT)
    write_response(client, "200 OK", "text/html", body.encode())


def handle_status(client):
    ok = camera is not None
    body = '{{"device":"{}","camera":{},"stream":"/stream"}}'.format(
        config.DEVICE_NAME,
        "true" if ok else "false",
    )
    write_response(client, "200 OK", "application/json", body.encode())


def handle_stream(client):
    if camera is None:
        write_response(
            client,
            "500 Internal Server Error",
            "text/plain",
            b"MicroPython firmware has no camera module. Flash ESP32-CAM camera firmware.",
        )
        return

    client.send(b"HTTP/1.1 200 OK\r\n")
    client.send(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n")
    client.send(b"Cache-Control: no-cache\r\n")
    client.send(b"Connection: close\r\n\r\n")

    while True:
        try:
            frame = camera.capture()
            if not frame:
                time.sleep(0.05)
                continue
            client.send(b"--" + BOUNDARY + b"\r\n")
            client.send(b"Content-Type: image/jpeg\r\n")
            client.send(("Content-Length: %d\r\n\r\n" % len(frame)).encode())
            client.send(frame)
            client.send(b"\r\n")
            gc.collect()
        except Exception as exc:
            print("stream stopped:", exc)
            break


def serve():
    wlan = connect_wifi()
    camera_ok = init_camera()
    ip = wlan.ifconfig()[0]
    addr = socket.getaddrinfo("0.0.0.0", config.STREAM_PORT)[0][-1]
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(2)
    print("device:", config.DEVICE_NAME)
    print("camera:", "ok" if camera_ok else "missing")
    print("stream: http://{}:{}/stream".format(ip, config.STREAM_PORT))

    while True:
        client, remote = server.accept()
        try:
            request = client.recv(512).decode("utf-8", "ignore")
            path = request.split(" ")[1] if request else "/"
            print(remote, path)
            if path.startswith("/stream"):
                handle_stream(client)
            elif path.startswith("/status"):
                handle_status(client)
            else:
                handle_root(client, ip)
        except Exception as exc:
            print("request failed:", exc)
        finally:
            try:
                client.close()
            except Exception:
                pass


serve()
