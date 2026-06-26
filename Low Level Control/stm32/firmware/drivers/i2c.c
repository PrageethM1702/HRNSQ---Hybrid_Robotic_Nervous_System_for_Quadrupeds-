#include <stdint.h>
#include <string.h>

static uint8_t i2c_memory[128][16];

void i2c_init(void)
{
    memset(i2c_memory, 0, sizeof(i2c_memory));
}

int i2c_write_register(uint8_t address, uint8_t reg, uint8_t value)
{
    if (address >= 128 || reg >= 16)
    {
        return -1;
    }
    i2c_memory[address][reg] = value;
    return 0;
}

int i2c_read_register(uint8_t address, uint8_t reg, uint8_t *value)
{
    if (address >= 128 || reg >= 16 || value == 0)
    {
        return -1;
    }
    *value = i2c_memory[address][reg];
    return 0;
}
