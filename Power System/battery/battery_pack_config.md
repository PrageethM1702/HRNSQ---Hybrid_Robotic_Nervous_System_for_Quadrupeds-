# Battery Pack Configuration

Nominal pack: 3S Li-ion or LiPo for prototype testing.

Voltage limits:

- Full charge: 12.6 V
- Nominal: 11.1 V
- Warning: 10.8 V
- Shutdown: 10.5 V

Power rails:

- VSYS from battery input through protection and switching.
- 5 V rail from LM2596 buck stage for modules that require 5 V.
- 3.3 V rail from AMS1117 or equivalent regulator for STM32 and logic.

Rules:

- Logic and power grounds must be common at the designed ground reference.
- 5 V peripherals must use level shifting before STM32 GPIO.
- Reflex unit comparator outputs must be pulled to 3.3 V logic.
