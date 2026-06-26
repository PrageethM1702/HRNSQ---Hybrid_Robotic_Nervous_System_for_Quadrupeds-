/* HRNS-Q Cortex M4 helper routines
 * Target: STM32F407 / ARM Cortex M4
 * Syntax: GNU assembler
 */

    .syntax unified
    .cpu cortex-m4
    .thumb

    .equ DEMCR,       0xE000EDFC
    .equ DWT_CTRL,    0xE0001000
    .equ DWT_CYCCNT,  0xE0001004
    .equ TRCENA_BIT,  0x01000000
    .equ CYCCNTENA,   0x00000001

    .section .text.hrnsq_helpers, "ax", %progbits

    .global hrnsq_irq_lock
    .type hrnsq_irq_lock, %function
hrnsq_irq_lock:
    mrs     r0, PRIMASK
    cpsid   i
    bx      lr
    .size hrnsq_irq_lock, . - hrnsq_irq_lock

    .global hrnsq_irq_restore
    .type hrnsq_irq_restore, %function
hrnsq_irq_restore:
    msr     PRIMASK, r0
    bx      lr
    .size hrnsq_irq_restore, . - hrnsq_irq_restore

    .global hrnsq_wait_for_interrupt
    .type hrnsq_wait_for_interrupt, %function
hrnsq_wait_for_interrupt:
    dsb
    wfi
    isb
    bx      lr
    .size hrnsq_wait_for_interrupt, . - hrnsq_wait_for_interrupt

    .global hrnsq_wait_for_event
    .type hrnsq_wait_for_event, %function
hrnsq_wait_for_event:
    dsb
    wfe
    isb
    bx      lr
    .size hrnsq_wait_for_event, . - hrnsq_wait_for_event

    .global hrnsq_cycle_counter_enable
    .type hrnsq_cycle_counter_enable, %function
hrnsq_cycle_counter_enable:
    ldr     r0, =DEMCR
    ldr     r1, [r0]
    ldr     r2, =TRCENA_BIT
    orr     r1, r1, r2
    str     r1, [r0]

    ldr     r0, =DWT_CYCCNT
    movs    r1, #0
    str     r1, [r0]

    ldr     r0, =DWT_CTRL
    ldr     r1, [r0]
    orr     r1, r1, #CYCCNTENA
    str     r1, [r0]
    bx      lr
    .size hrnsq_cycle_counter_enable, . - hrnsq_cycle_counter_enable

    .global hrnsq_cycle_counter_read
    .type hrnsq_cycle_counter_read, %function
hrnsq_cycle_counter_read:
    ldr     r1, =DWT_CYCCNT
    ldr     r0, [r1]
    bx      lr
    .size hrnsq_cycle_counter_read, . - hrnsq_cycle_counter_read
