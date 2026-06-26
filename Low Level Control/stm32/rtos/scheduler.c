#include <stdint.h>

typedef void (*TaskFn)(void);

typedef struct
{
    TaskFn fn;
    uint32_t period_ms;
    uint32_t elapsed_ms;
} TaskSlot;

static TaskSlot tasks[8];
static uint8_t task_count;

void scheduler_init(void)
{
    task_count = 0;
}

int scheduler_add(TaskFn fn, uint32_t period_ms)
{
    if (task_count >= 8 || fn == 0 || period_ms == 0)
    {
        return -1;
    }
    tasks[task_count].fn = fn;
    tasks[task_count].period_ms = period_ms;
    tasks[task_count].elapsed_ms = 0;
    task_count++;
    return 0;
}

void scheduler_step(uint32_t dt_ms)
{
    for (uint8_t i = 0; i < task_count; i++)
    {
        tasks[i].elapsed_ms += dt_ms;
        if (tasks[i].elapsed_ms >= tasks[i].period_ms)
        {
            tasks[i].elapsed_ms = 0;
            tasks[i].fn();
        }
    }
}

void scheduler_tick(void)
{
    scheduler_step(1);
}
