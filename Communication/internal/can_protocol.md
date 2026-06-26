# CAN Protocol

| ID | Direction | Payload |
| --- | --- | --- |
| 0x101 | Reflex to master | FL contact, overload, slip, FSR voltage |
| 0x102 | Reflex to master | FR contact, overload, slip, FSR voltage |
| 0x103 | Reflex to master | RL contact, overload, slip, FSR voltage |
| 0x104 | Reflex to master | RR contact, overload, slip, FSR voltage |
| 0x201 | Master to reflex | threshold voltage, CPG frequency, reflex gain |
| 0x301 | Safety to all | stop mode, motor disable, reason code |

All logic-level interface signals are referenced to common ground. Comparator outputs must be interpreted as 3.3 V digital signals after pull-up and Schmitt cleanup.
