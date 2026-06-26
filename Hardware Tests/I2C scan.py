import smbus2

bus = smbus2.SMBus(1)

print("Scanning I2C bus...\n")

devices = []

for address in range(0x03, 0x78):
    try:
        bus.write_quick(address)
        devices.append(address)
    except:
        pass

bus.close()

if devices:
    print("Found devices:")
    for addr in devices:
        print(f" - 0x{addr:02X}")
else:
    print("No I2C devices found")
