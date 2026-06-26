#include "main.h"
#include <stdio.h>

extern ADC_HandleTypeDef hadc1;
extern UART_HandleTypeDef huart2;

#define ADC_RESOLUTION 4095.0f
#define VREF 3.3f

#define DIV_BAT 11.0f
#define DIV_8V  4.0f
#define DIV_5V  2.0f
#define DIV_3V3 1.0f

#define SHUNT_RES 0.05f
#define SHUNT_GAIN 20.0f

#define BAT_LOW 10.5f
#define V5_MIN 4.7f
#define V3_MIN 3.1f
#define SERVO_CURR_MAX 10.0f

uint32_t read_adc(uint32_t channel)
{
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, HAL_MAX_DELAY);
    return HAL_ADC_GetValue(&hadc1);
}

float adc_to_voltage(uint32_t adc)
{
    return (adc * VREF) / ADC_RESOLUTION;
}
float read_voltage(uint32_t channel, float divider)
{
    return adc_to_voltage(read_adc(channel)) * divider;
}
float read_current(uint32_t channel)
{
    float v = adc_to_voltage(read_adc(channel));
    return v / (SHUNT_RES * SHUNT_GAIN);
}

void uart_print(char *msg)
{
    HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
}
void power_monitor_task(void)
{
    char buffer[128];

    float v_bat = read_voltage(ADC_CHANNEL_0, DIV_BAT);
    float v_8   = read_voltage(ADC_CHANNEL_1, DIV_8V);
    float v_5   = read_voltage(ADC_CHANNEL_2, DIV_5V);
    float v_3   = read_voltage(ADC_CHANNEL_3, DIV_3V3);
    float i_srv = read_current(ADC_CHANNEL_4);

    sprintf(buffer, "BAT: %.2f V | 8V: %.2f V | 5V: %.2f V | 3V3: %.2f V | SERVO_I: %.2f A\r\n",
            v_bat, v_8, v_5, v_3, i_srv);
    uart_print(buffer);

    if(v_bat < BAT_LOW)
        uart_print("FAULT: BATTERY LOW !\r\n");

    if(v_5 < V5_MIN)
        uart_print("FAULT: 5V UNDERVOLTAGE !\r\n");

    if(v_3 < V3_MIN)
        uart_print("FAULT: 3V3 UNDERVOLTAGE !\r\n");

    if(i_srv > SERVO_CURR_MAX)
        uart_print("FAULT: SERVO OVERCURRENT !\r\n");
}
