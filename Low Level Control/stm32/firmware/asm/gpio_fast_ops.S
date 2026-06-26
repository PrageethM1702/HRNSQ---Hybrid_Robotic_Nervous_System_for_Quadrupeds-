/* HRNS-Q fast GPIO operations for STM32 GPIOx_BSRR
 * r0: GPIO peripheral base address
 * r1: pin mask, for example 1 << 5
 */

    .syntax unified
    .cpu cortex-m4
    .thumb

    .equ GPIO_BSRR_OFFSET, 0x18

    .section .text.hrnsq_gpio_fast_ops, "ax", %progbits

    .global hrnsq_gpio_set
    .type hrnsq_gpio_set, %function
hrnsq_gpio_set:
    str     r1, [r0, #GPIO_BSRR_OFFSET]
    bx      lr
    .size hrnsq_gpio_set, . - hrnsq_gpio_set

    .global hrnsq_gpio_clear
    .type hrnsq_gpio_clear, %function
hrnsq_gpio_clear:
    lsls    r1, r1, #16
    str     r1, [r0, #GPIO_BSRR_OFFSET]
    bx      lr
    .size hrnsq_gpio_clear, . - hrnsq_gpio_clear

    .global hrnsq_gpio_pulse
    .type hrnsq_gpio_pulse, %function
hrnsq_gpio_pulse:
    str     r1, [r0, #GPIO_BSRR_OFFSET]
    lsls    r1, r1, #16
    str     r1, [r0, #GPIO_BSRR_OFFSET]
    bx      lr
    .size hrnsq_gpio_pulse, . - hrnsq_gpio_pulse
