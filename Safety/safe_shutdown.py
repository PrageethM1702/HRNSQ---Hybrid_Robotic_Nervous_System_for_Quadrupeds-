import asyncio

class SafeShutdown:
    def __init__(self):
        self.shutdown_triggered = False

    async def execute_shutdown(self, actuators, power):
        if self.shutdown_triggered:
            return
        self.shutdown_triggered = True
        for name in actuators:
            actuators[name] = 0
        for name in power:
            power[name] = 0
        await asyncio.sleep(0.1)
        print("System safely shutdown")
