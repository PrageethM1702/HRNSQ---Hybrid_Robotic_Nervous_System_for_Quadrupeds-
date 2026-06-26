# STM32 Cortex M4 Assembly Helpers

These files are optional low-level assembly helpers for the STM32F407 reflex
controller side of HRNS-Q.

They are written for GNU Arm Embedded Toolchain syntax and can be assembled as
`.S` files in STM32CubeIDE or a Makefile based firmware project.

## Files

| File | Purpose |
|---|---|
| `cortex_m4_helpers.S` | Interrupt masking, wait states, cycle counter enable and cycle reads |
| `gpio_fast_ops.S` | Fast atomic GPIO bit set/reset helpers using STM32 BSRR registers |
| `reflex_irq_stub.S` | Minimal EXTI interrupt stub pattern for fast reflex signal entry |
| `startup_hrnsq_f407_template.S` | Startup/vector table template for STM32F407VETx projects |

## Notes

These files are not required for the Raspberry Pi dashboard or PCA9685 servo
demo. They are included to support the embedded reflex layer where deterministic
latency matters.

Typical C prototypes:

```c
uint32_t hrnsq_irq_lock(void);
void hrnsq_irq_restore(uint32_t primask);
void hrnsq_wait_for_interrupt(void);
void hrnsq_wait_for_event(void);
void hrnsq_cycle_counter_enable(void);
uint32_t hrnsq_cycle_counter_read(void);
void hrnsq_gpio_set(void *gpio_base, uint32_t pin_mask);
void hrnsq_gpio_clear(void *gpio_base, uint32_t pin_mask);
```

For final STM32CubeIDE use, keep only one startup file in the build. If CubeMX
generates a startup file, use this template as a reference instead of compiling
both startup files.

## STM32CubeIDE Integration

1. Copy the `.S` and hook files into the STM32 firmware project.
2. Add `hrnsq_asm_hooks.h` to the include path used by the C files.
3. Include `hrnsq_asm_hooks.h` from C modules that need fast IRQ locking,
   GPIO toggles or cycle timing.
4. Compile either the CubeMX generated startup file or
   `startup_hrnsq_f407_template.S`, not both.
