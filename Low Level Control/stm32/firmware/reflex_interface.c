#include <stdint.h>

typedef struct
{
    uint8_t contact;
    uint8_t overload;
    uint8_t slip;
    float fsr_voltage;
    float threshold_voltage;
    float reflex_gain;
    float cpg_frequency;
} ReflexChannel;

static float clampf(float value, float low, float high)
{
    if (value < low)
    {
        return low;
    }
    if (value > high)
    {
        return high;
    }
    return value;
}

void reflex_channel_init(ReflexChannel *channel)
{
    channel->contact = 0U;
    channel->overload = 0U;
    channel->slip = 0U;
    channel->fsr_voltage = 0.0f;
    channel->threshold_voltage = 1.0f;
    channel->reflex_gain = 0.35f;
    channel->cpg_frequency = 1.5f;
}

void reflex_channel_update(ReflexChannel *channel, float fsr_voltage, uint8_t comparator_state)
{
    channel->fsr_voltage = clampf(fsr_voltage, 0.0f, 3.3f);
    channel->contact = comparator_state ? 1U : 0U;
    channel->overload = channel->fsr_voltage > 1.2f ? 1U : 0U;
    channel->slip = channel->contact && channel->fsr_voltage < channel->threshold_voltage * 0.65f ? 1U : 0U;
}

float reflex_threshold_to_dac(float threshold_voltage)
{
    return clampf(threshold_voltage, 0.0f, 3.3f) / 3.3f;
}

float reflex_cpg_frequency_to_dac(float frequency_hz)
{
    return clampf((frequency_hz - 0.5f) / 2.5f, 0.0f, 1.0f);
}

float reflex_motor_bias(const ReflexChannel *channel)
{
    if (channel->overload)
    {
        return -0.6f * channel->reflex_gain;
    }
    if (channel->slip)
    {
        return 0.25f * channel->reflex_gain;
    }
    if (channel->contact)
    {
        return -0.3f * channel->reflex_gain;
    }
    return 0.0f;
}
