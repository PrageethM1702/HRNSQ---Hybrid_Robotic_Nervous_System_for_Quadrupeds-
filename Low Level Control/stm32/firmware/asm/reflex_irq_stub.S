/* HRNS-Q reflex interrupt stub
 * This is a minimal EXTI entry pattern for fast reflex signal capture.
 * The actual handler should clear the EXTI pending bit in C or in a board
 * specific assembly routine after reading the active line.
 */

    .syntax unified
    .cpu cortex-m4
    .thumb

    .extern hrnsq_reflex_irq_fast_path

    .section .text.hrnsq_reflex_irq, "ax", %progbits

    .global EXTI0_IRQHandler
    .type EXTI0_IRQHandler, %function
EXTI0_IRQHandler:
    push    {r0-r3, r12, lr}
    movs    r0, #0
    bl      hrnsq_reflex_irq_fast_path
    pop     {r0-r3, r12, lr}
    bx      lr
    .size EXTI0_IRQHandler, . - EXTI0_IRQHandler

    .global EXTI1_IRQHandler
    .type EXTI1_IRQHandler, %function
EXTI1_IRQHandler:
    push    {r0-r3, r12, lr}
    movs    r0, #1
    bl      hrnsq_reflex_irq_fast_path
    pop     {r0-r3, r12, lr}
    bx      lr
    .size EXTI1_IRQHandler, . - EXTI1_IRQHandler

    .global EXTI2_IRQHandler
    .type EXTI2_IRQHandler, %function
EXTI2_IRQHandler:
    push    {r0-r3, r12, lr}
    movs    r0, #2
    bl      hrnsq_reflex_irq_fast_path
    pop     {r0-r3, r12, lr}
    bx      lr
    .size EXTI2_IRQHandler, . - EXTI2_IRQHandler

    .global EXTI3_IRQHandler
    .type EXTI3_IRQHandler, %function
EXTI3_IRQHandler:
    push    {r0-r3, r12, lr}
    movs    r0, #3
    bl      hrnsq_reflex_irq_fast_path
    pop     {r0-r3, r12, lr}
    bx      lr
    .size EXTI3_IRQHandler, . - EXTI3_IRQHandler
