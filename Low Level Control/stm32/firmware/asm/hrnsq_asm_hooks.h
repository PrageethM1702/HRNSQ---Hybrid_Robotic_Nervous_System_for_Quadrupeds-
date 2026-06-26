#ifndef HRNSQ_ASM_HOOKS_H
#define HRNSQ_ASM_HOOKS_H

#include <stdint.h>

uint32_t hrnsq_irq_lock(void);
void hrnsq_irq_restore(uint32_t primask);
void hrnsq_wait_for_interrupt(void);
void hrnsq_wait_for_event(void);
void hrnsq_cycle_counter_enable(void);
uint32_t hrnsq_cycle_counter_read(void);

void hrnsq_gpio_set(void *gpio_base, uint32_t pin_mask);
void hrnsq_gpio_clear(void *gpio_base, uint32_t pin_mask);
void hrnsq_gpio_pulse(void *gpio_base, uint32_t pin_mask);

void hrnsq_reflex_irq_fast_path(uint32_t reflex_line);

#endif
