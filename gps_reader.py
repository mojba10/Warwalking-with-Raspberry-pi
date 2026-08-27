import serial
import pynmea2
import time
import logging

def read_gps(port='/dev/serial0', baudrate=9600, timeout=1, max_wait=15):
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
            start_time = time.time()
            while True:
                if time.time() - start_time > max_wait:
                    print("Timeout")
                    return None
                line = ser.readline().decode('ascii', errors='replace').strip()

                if line.startswith("$GNRMC") or line.startswith("$GPRMC"):
                    try:
                        gps = pynmea2.parse(line)
                        if gps.status == 'A':
                            return {
                                'latitude': gps.latitude,
                                'longitude': gps.longitude
                            }
                        
                    except pynmea2.ParseError:
                        continue

    except serial.SerialException as e:
        logging.log(2,f"Error for connecting to GPS: {e}")
        return None

    except KeyboardInterrupt:
        raise
