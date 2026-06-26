# PCA9685 8-Servo Wiring

HRNS-Q uses eight 180-degree hobby servos through one PCA9685 PWM driver.
Hip motors are not used in the current build; only shoulder and knee joints are driven.

## PCA9685 to Raspberry Pi 3

| PCA9685 pin | Raspberry Pi 3 pin | Notes |
|---|---|---|
| VCC | Pin 1, 3.3 V | PCA9685 logic supply |
| GND | Pin 6, GND | Common ground |
| SDA | Pin 3, GPIO2/SDA1 | I2C data |
| SCL | Pin 5, GPIO3/SCL1 | I2C clock |
| OE | GND or leave enabled on breakout | Pull high only for emergency PWM disable |
| V+ | External 5-6 V servo supply | Do not power servos from Pi 5 V pin |

Connect the external servo supply ground to PCA9685 GND and Raspberry Pi GND.

## Servo Channel Map

| PCA9685 channel | Leg | Joint | Software command |
|---:|---|---|---|
| 0 | Front left | Shoulder | `FL.shoulder_deg` |
| 1 | Front left | Knee | `FL.knee_deg` |
| 2 | Front right | Shoulder | `FR.shoulder_deg` |
| 3 | Front right | Knee | `FR.knee_deg` |
| 4 | Rear left | Shoulder | `RL.shoulder_deg` |
| 5 | Rear left | Knee | `RL.knee_deg` |
| 6 | Rear right | Shoulder | `RR.shoulder_deg` |
| 7 | Rear right | Knee | `RR.knee_deg` |

## Servo Connector

| Servo wire | PCA9685 / supply |
|---|---|
| Signal | PCA9685 channel signal pin |
| Red / V+ | External 5-6 V servo supply through PCA9685 V+ rail |
| Brown/black / GND | PCA9685 GND and external supply GND |

Before attaching legs, run the neutral pose and confirm all servos sit at the intended 90-degree mechanical center.
