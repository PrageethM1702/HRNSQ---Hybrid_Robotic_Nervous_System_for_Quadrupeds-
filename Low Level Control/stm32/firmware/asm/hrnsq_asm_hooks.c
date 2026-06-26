#include "hrnsq_asm_hooks.h"

volatile uint32_t hrnsq_reflex_irq_count[4];

void hrnsq_reflex_irq_fast_path(uint32_t reflex_line)
{
    if (reflex_line < 4U)
    {
        hrnsq_reflex_irq_count[reflex_line]++;
    }
}
