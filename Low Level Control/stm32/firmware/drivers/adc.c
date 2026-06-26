#include <stdint.h>

static uint16_t adc_channels[16];
static uint8_t adc_count;

void adc_init(uint8_t channels)
{
    adc_count = channels > 16 ? 16 : channels;
    for (uint8_t i = 0; i < adc_count; i++)
    {
        adc_channels[i] = 0;
    }
}

void adc_set_sample(uint8_t channel, uint16_t value)
{
    if (channel < adc_count)
    {
        adc_channels[channel] = value;
    }
}

uint16_t adc_read(uint8_t channel)
{
    if (channel >= adc_count)
    {
        return 0;
    }
    return adc_channels[channel];
}

float adc_to_voltage(uint16_t sample, float reference)
{
    return ((float)sample * reference) / 4095.0f;
}
