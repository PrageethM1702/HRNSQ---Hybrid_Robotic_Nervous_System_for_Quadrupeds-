# HRNS-Q Dashboard Run Guide

The dashboard supports two telemetry sources:

- `Sim`: generated telemetry for demo and UI testing.
- `Real`: Raspberry Pi hardware telemetry, PCA9685 actuator commands, night camera stream, and ESP32 stereo heat view.

## Ports

| Function | Port |
|---|---:|
| Dashboard page | 5500 |
| Telemetry WebSocket | 9001 |
| Vision streams | 9100 |
| ESP32-CAM left stream | device IP, usually 81 |
| ESP32-CAM right stream | device IP, usually 81 |

## Start On Raspberry Pi

Terminal 1, vision service:

```bash
cd ~/HRNS-Q/Perception/Depth\ Camera
export HRNSQ_ESP32_LEFT_URL="http://192.168.1.51:81/stream"
export HRNSQ_ESP32_RIGHT_URL="http://192.168.1.52:81/stream"
export HRNSQ_NIGHT_CAM_INDEX="0"
python stereo_heat_server.py
```

Terminal 2, telemetry service:

```bash
cd ~/HRNS-Q
source hrnsq_env/bin/activate
cd "Software Framework/interface"
python websocket_server.py
```

Terminal 3, dashboard page:

```bash
cd ~/HRNS-Q/Software\ Framework/interface/dashboard
python -m http.server 5500 --bind 0.0.0.0
```

Open:

```text
http://<raspberry-pi-ip>:5500/templates/dashboard.html
```

Click `Sim` or `Real` in the dashboard header.

## Servo Safety

Real mode reads sensors and streams cameras by default. It does not move servos unless enabled.

To enable PCA9685 servo output:

```bash
export HRNSQ_ENABLE_SERVOS=1
python websocket_server.py
```

Keep the robot lifted during first tests.
