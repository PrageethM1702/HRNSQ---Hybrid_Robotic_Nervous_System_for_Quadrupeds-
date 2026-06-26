# HRNS-Q Architecture Description

HRNS-Q is a hybrid robotic nervous system for a quadruped robot. The project combines fast analog reflex paths with a slower digital cognition layer so the robot can react immediately to contact, overload, slip and obstacles while still using AI for gait selection, terrain understanding and high-level navigation.

The selected methodology uses analog reflex circuits for time-critical response. Foot contact is sensed by FSR or piezo sensors in divider networks and compared with adjustable thresholds through LM339 or LM393 comparator stages. The comparator outputs are open-collector signals and are cleaned through 74HC14 Schmitt trigger stages before entering STM32F407VETx GPIO pins. Firmware must use pull-up or pull-down configuration and must treat these signals as 3.3 V logic only.

The digital layer does not directly replace the reflex path. STM32 and AI modules modulate comparator thresholds, CPG frequency, gait amplitude and reflex gain. The cognitive loop runs at a slower rate than the reflex loop and uses IMU, encoder, pressure and vision information to tune the analog nervous system.

Main layers:

- Low-level reflex layer: FSR/contact interrupts, overload detection, slip detection and safe override.
- CPG layer: walk, trot, pace and bound phase tables with 1-2 Hz baseline gait timing.
- Neural layer: gait adaptation, sensor fusion, vision terrain classification, reflex modulation and decision policy.
- Cognition layer: navigation, exploration, behavior state machine and task selection.
- Safety layer: battery, temperature, communication timeout, tilt and emergency shutdown supervision.

Electrical rules from the reflex unit design:

- All grounds must be common.
- No 5 V signal may enter STM32 GPIO.
- GPIO maximum should be treated as 3.6 V with recommended current below 5 mA.
- LM339 outputs require pull-up resistors because they cannot source current.
- 74HC14 inputs must never float.
- FSR divider voltage into comparator stages should stay below the safe input range.
- Wiper disconnect conditions need a safe default path to ground.
