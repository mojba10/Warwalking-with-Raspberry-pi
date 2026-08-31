#!/usr/bin/env python3
# gps_test.py - Test NEO-6M GPS module connection on Raspberry Pi

# if you get Permisson Error Run "sudo usermod -a -G dialout $USER"
# After that you have to see file like /dev/ttyAMA0 Or /dev/ttyS0
import serial
import time

# Serial port settings
GPS_PORT = "/dev/ttyAMA0"  # if Bluetooth is disabled
# GPS_PORT = "/dev/ttyS0"  # if using mini UART
GPS_BAUDRATE = 9600

def parse_gprmc(sentence):
    """Parse GPRMC sentence to get position"""
    parts = sentence.split(',')
    if len(parts) < 7:
        return None

    status = parts[2]  # A = active, V = warning (weak signal)
    if status != 'A':
        return None

    lat_raw  = parts[3]
    lat_dir  = parts[4]
    lon_raw  = parts[5]
    lon_dir  = parts[6]

    if not lat_raw or not lon_raw:
        return None

    # NMEA format: DDDMM.MMMM -> convert to decimal
    lat_deg  = float(lat_raw[:2])
    lat_min  = float(lat_raw[2:])
    latitude = lat_deg + lat_min / 60
    if lat_dir == 'S':
        latitude = -latitude

    lon_deg   = float(lon_raw[:3])
    lon_min   = float(lon_raw[3:])
    longitude = lon_deg + lon_min / 60
    if lon_dir == 'W':
        longitude = -longitude

    return {
        "latitude":  round(latitude,  6),
        "longitude": round(longitude, 6),
        "time_utc":  parts[1]
    }

def parse_gpgga(sentence):
    """Parse GPGGA sentence to get altitude and satellite count"""
    parts = sentence.split(',')
    if len(parts) < 10:
        return None

    fix_quality = parts[6]
    if fix_quality == '0':
        return None

    num_satellites = parts[7]
    altitude       = parts[9]
    alt_unit       = parts[10] if len(parts) > 10 else 'M'

    return {
        "satellites": int(num_satellites) if num_satellites else 0,
        "altitude":   f"{altitude} {alt_unit}" if altitude else "N/A"
    }

def read_gps():
    try:
        ser = serial.Serial(GPS_PORT, baudrate=GPS_BAUDRATE, timeout=1)
        print(f"Port {GPS_PORT} opened successfully\n")
        print("Waiting for GPS data...")
        print("(If you're indoors, it may take a few minutes to get a fix)\n")
        print("-" * 45)

        location = None
        extra    = None

        while True:
            try:
                line = ser.readline().decode('ascii', errors='ignore').strip()

                if line.startswith('$GPRMC'):
                    location = parse_gprmc(line)
                    if location:
                        print(f"Location:")
                        print(f"   Latitude  : {location['latitude']}")
                        print(f"   Longitude : {location['longitude']}")
                        print(f"   UTC time  : {location['time_utc']}")

                elif line.startswith('$GPGGA'):
                    extra = parse_gpgga(line)
                    if extra:
                        print(f"   Satellites: {extra['satellites']}")
                        print(f"   Altitude  : {extra['altitude']}")
                        print("-" * 45)

                # print raw NMEA sentences for debugging
                # print(line)

            except UnicodeDecodeError:
                pass

    except serial.SerialException as e:
        print(f"Error opening port: {e}")
        print("\nPossible solutions:")
        print("  1. Make sure UART is enabled in raspi-config")
        print("  2. sudo raspi-config -> Interface Options -> Serial Port")
        print("     -> login shell: No  |  serial port hardware: Yes")
        print("  3. Check the port: ls /dev/tty*")
    except KeyboardInterrupt:
        print("\n\nStopped.")
        ser.close()

if __name__ == "__main__":
    read_gps()