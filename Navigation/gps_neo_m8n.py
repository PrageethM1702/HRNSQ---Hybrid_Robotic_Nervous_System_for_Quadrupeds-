import serial
import pynmea2
import time

# /dev/serial0 points to GPIO 14/15 (UART)
# Baud rate for NEO-6M is usually 9600
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout = 1)

def read_gps():
    try:
        line = ser.readline().decode('ascii', errors = 'replace')
        if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
            msg = pynmea2.parse(line)
            data = {
                "latitude": msg.latitude,
                "longitude": msg.longitude,
                "timestamp": msg.timestamp if hasattr(msg, "timestamp") else None,
                "altitude": getattr(msg, "altitude", None),
                "num_sats": getattr(msg, "num_sats", None)
            }
            return data
    except pynmea2.ParseError:
        return None
    return None

if __name__ == "__main__":
    while True:
        gps_data = read_gps()
        if gps_data:
            print(f"GPS Data: {gps_data}")
        else:
            print("Waiting for GPS fix...")
        time.sleep(1)
