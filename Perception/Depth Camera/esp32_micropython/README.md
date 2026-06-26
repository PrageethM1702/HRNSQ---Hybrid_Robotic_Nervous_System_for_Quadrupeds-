# ESP32-CAM MicroPython Streamer

Use this folder for the two ESP32-CAM boards when Arduino is not allowed.

Important: the ESP32-CAM must be flashed with a MicroPython firmware build that
includes the `camera` module. Standard ESP32 MicroPython firmware often does
not include camera support. After flashing, connect to REPL and test:

```python
import camera
```

If that fails, the firmware is wrong for ESP32-CAM camera streaming.

## Files

| File | Purpose |
|---|---|
| `main.py` | MJPEG camera stream server |
| `config_left.py` | Left ESP32-CAM settings |
| `config_right.py` | Right ESP32-CAM settings |

Before uploading, copy either `config_left.py` or `config_right.py` to
`config.py`, then edit Wi-Fi details.

## Flash Firmware

Install tools on your PC:

```powershell
python -m pip install esptool mpremote
```

Put ESP32-CAM in flash mode:

| ESP32-CAM pin | Connect |
|---|---|
| IO0 | GND while flashing |
| U0R/RX | USB-TTL TX |
| U0T/TX | USB-TTL RX |
| GND | USB-TTL GND |
| 5V | Stable 5 V |

Erase:

```powershell
python -m esptool --chip esp32 --port COM5 erase_flash
```

Flash MicroPython ESP32-CAM firmware:

```powershell
python -m esptool --chip esp32 --port COM5 --baud 460800 write_flash -z 0x1000 ESP32_CAM_MICROPYTHON_CAMERA.bin
```

Remove IO0 from GND, press reset, then upload files.

## Upload Left Camera

```powershell
copy config_left.py config.py
mpremote connect COM5 fs cp config.py :
mpremote connect COM5 fs cp main.py :
mpremote connect COM5 reset
```

## Upload Right Camera

```powershell
copy config_right.py config.py
mpremote connect COM6 fs cp config.py :
mpremote connect COM6 fs cp main.py :
mpremote connect COM6 reset
```

Serial output prints the stream URL:

```text
stream: http://192.168.1.51:81/stream
```

Use these URLs on the Raspberry Pi:

```bash
export HRNSQ_ESP32_LEFT_URL="http://192.168.1.51:81/stream"
export HRNSQ_ESP32_RIGHT_URL="http://192.168.1.52:81/stream"
```

## Notes

- Use a stable 5 V supply. ESP32-CAM brownouts are common.
- Keep both ESP32-CAMs on the same Wi-Fi network as the Raspberry Pi.
- For your current prototype, the Raspberry Pi creates the heat/depth view.
  The ESP32-CAMs only stream JPEG frames.
