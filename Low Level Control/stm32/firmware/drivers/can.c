#include <stdint.h>
#include <string.h>

typedef struct
{
    uint32_t id;
    uint8_t length;
    uint8_t data[8];
} CanFrame;

static CanFrame last_tx;
static CanFrame last_rx;

void can_init(void)
{
    memset(&last_tx, 0, sizeof(last_tx));
    memset(&last_rx, 0, sizeof(last_rx));
}

int can_send(uint32_t id, const uint8_t *data, uint8_t length)
{
    if (length > 8)
    {
        return -1;
    }
    last_tx.id = id;
    last_tx.length = length;
    memcpy(last_tx.data, data, length);
    return 0;
}

int can_receive(CanFrame *frame)
{
    if (frame == 0)
    {
        return -1;
    }
    *frame = last_rx;
    return last_rx.length > 0 ? 1 : 0;
}

void can_mock_receive(uint32_t id, const uint8_t *data, uint8_t length)
{
    if (length > 8)
    {
        length = 8;
    }
    last_rx.id = id;
    last_rx.length = length;
    memcpy(last_rx.data, data, length);
}
