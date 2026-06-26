#include <stdint.h>

void adc_init(uint8_t channels);
void pwm_init(uint32_t frequency_hz);
void can_init(void);
void i2c_init(void);
void reflex_interface_init(void);
void scheduler_init(void);
void scheduler_tick(void);
void watchdog_init(uint32_t timeout_ms);
void watchdog_kick(void);

int main(void)
{
    adc_init(12);
    pwm_init(20000);
    can_init();
    i2c_init();
    reflex_interface_init();
    scheduler_init();
    watchdog_init(250);
    while (1)
    {
        scheduler_tick();
        watchdog_kick();
    }
    return 0;
}
