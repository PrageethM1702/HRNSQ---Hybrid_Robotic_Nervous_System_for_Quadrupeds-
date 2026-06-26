#include <stdint.h>

static float pwm_duty[16];
static uint32_t pwm_frequency;

void pwm_init(uint32_t frequency_hz)
{
    pwm_frequency = frequency_hz;
    for (uint8_t i = 0; i < 16; i++)
    {
        pwm_duty[i] = 0.0f;
    }
}

void pwm_set_duty(uint8_t channel, float duty)
{
    if (channel >= 16)
    {
        return;
    }
    if (duty < 0.0f)
    {
        duty = 0.0f;
    }
    if (duty > 1.0f)
    {
        duty = 1.0f;
    }
    pwm_duty[channel] = duty;
}

float pwm_get_duty(uint8_t channel)
{
    if (channel >= 16)
    {
        return 0.0f;
    }
    return pwm_duty[channel];
}

uint32_t pwm_get_frequency(void)
{
    return pwm_frequency;
}
