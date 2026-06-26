#include <stdint.h>

static uint32_t watchdog_timeout;
static uint32_t watchdog_counter;
static uint8_t watchdog_fault;

void watchdog_init(uint32_t timeout_ms)
{
    watchdog_timeout = timeout_ms;
    watchdog_counter = 0;
    watchdog_fault = 0;
}

void watchdog_kick(void)
{
    watchdog_counter = 0;
    watchdog_fault = 0;
}

void watchdog_step(uint32_t dt_ms)
{
    watchdog_counter += dt_ms;
    if (watchdog_counter > watchdog_timeout)
    {
        watchdog_fault = 1;
    }
}

uint8_t watchdog_has_fault(void)
{
    return watchdog_fault;
}
