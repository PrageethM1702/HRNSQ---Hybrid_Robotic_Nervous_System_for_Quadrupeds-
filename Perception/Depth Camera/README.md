# HRNS-Q Depth Camera And Human Reaction

This folder contains the practical vision service for the current prototype.

It is not an accurate calibrated stereo-depth system. The two ESP32-CAMs are
mounted 15 cm apart and 6 cm from the ground, so this service produces a
simple heat/depth-like view for dashboard demonstration. It also reads the
wide-angle night-vision camera and performs lightweight face/upper-body
detection for human-reactive behavior.

## Ports

| Service | Port / URL |
|---|---|
| Dashboard web page | `http://<pi-ip>:5500/templates/dashboard.html` |
| Telemetry WebSocket | `ws://<pi-ip>:9001` |
| Vision stream service | `http://<pi-ip>:9100` |
| ESP32-CAM left | `http://<left-esp32-ip>:81/stream` |
| ESP32-CAM right | `http://<right-esp32-ip>:81/stream` |

## Environment Variables

Set these on the Raspberry Pi before starting the vision service:

```bash
export HRNSQ_ESP32_LEFT_URL="http://192.168.1.51:81/stream"
export HRNSQ_ESP32_RIGHT_URL="http://192.168.1.52:81/stream"
export HRNSQ_NIGHT_CAM_INDEX="0"
```

If the night-vision camera appears as another USB camera, change
`HRNSQ_NIGHT_CAM_INDEX` to `1` or `2`.

## Start

```bash
cd ~/HRNS-Q/10\ Perception/Depth\ Camera
python stereo_heat_server.py
```

Dashboard stream URLs:

```text
http://<pi-ip>:9100/night.mjpg
http://<pi-ip>:9100/depth_heat.mjpg
http://<pi-ip>:9100/reaction.json
```

## Human Reaction Mapping

| Detection | Robot reaction |
|---|---|
| Face high in frame | `look_up` |
| Face/person centered and close | `give_hand` |
| Face/person detected normally | `look_at_human` |
| Nothing detected | `idle_scan` |

These reactions are published as JSON and can be shown by the dashboard or
used by the Raspberry Pi command layer.
