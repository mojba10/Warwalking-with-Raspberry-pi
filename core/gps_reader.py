import time
import serial
import pynmea2
import logging
from config import GPS_PORT, GPS_BAUDRATE, GPS_TIMEOUT, GPS_MAX_WAIT

def read_gps (port: str=GPS_PORT, baudrate: int=GPS_BAUDRATE, timeout: int=GPS_TIMEOUT, max_wait: int=GPS_MAX_WAIT) -> dict | None: 
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
            start_time = time.time()
            while True:
                if time.time() - start_time > max_wait:
                    print("Timeout for gps!")
                    return None
                line = ser.readline().decode('ascii', errors='replace').strip()
                
                if line.startswith('$GNRMC') or line.startswith('$GPRMC'):
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
        logging.error(f"Error for connecting to GPS: {e}")
        return None
        
    except KeyboardInterrupt:
        raise
