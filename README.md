# Warwalking
 
A Raspberry Pi tool that scans nearby Wi-Fi networks, tags each one with a GPS location, evaluates its security, flags possible Evil-Twin attacks, and shows everything on a live map through a small web dashboard.
 
## Features
 
- **Wi-Fi scanning** — shows SSID, BSSID, channel, signal, encryption type of each Wi-Fi, via `nmcli`.
- **GPS tagging** — every scan is linked to the coordinates where it happened.
- **Security scoring** — combines encryption strength, default vendor SSID , and a dictionary attack with `aircrack-ng` into a single risk score.
- **Evil-Twin detection** — flags suspicious access points using:
  - Conflicting security type / vendor for the same SSID in one scan
  - Comparison with scan history (Is this BSSID, new for a known SSID?)
  - Distance and time proximity to the last known AP with that SSID
  - ESS awareness, so legitimate multi-AP setups (offices, malls) aren't falsely flagged
- **Web dashboard** — a live map and table, switchable between the current scan and full history.
## Project Structure
 
```
main.py
wordlist.txt
core/
  config.py              # all tunable settings in one place
  wifi_scanner.py        # nmcli-based scanning
  gps_reader.py          # serial GPS reading (NMEA)
  security_analyzer.py   # risk scoring
  evil_twin_detector.py  # evil-twin detection logic
database/
  db_manager.py          # SQLite storage (AP + scan history tables)
web/
  app.py                 # Flask backend
  templates/index.html   # map (Leaflet.js) + table frontend 
```
 
## Requirements
 
- Raspberry Pi (or any Linux machine) with a Wi-Fi adapter
- A GPS module connected via UART
- Python 3, plus:
```
  pip install pandas pyserial pynmea2 flask
```
- System tools: `network-manager`, `aircrack-ng`

## Note

In this project it is used raspberry pi 4 that have an internal wireless network card. But for better scanning we must use external Wi-Fi adapter connected to USB port. Also for using `aircrack-ng` tool we have to change interface to monitor mode that is another reason for using Wi-Fi adapter.

## Setup
 
1. Edit `core/config.py` — set your Wi-Fi interface name, GPS port, database path, and wordlist path.
2. Make sure the GPS module is working (go to note.txt in /GPS_config) and also `nmcli` can see your Wi-Fi interface.
3. Run:
```bash
   python main.py
```
   This scans, analyzes, saves everything to SQLite, and starts the web dashboard at `http://<device-ip>:5000`.
 
## Disclaimer
 
The password-auditing feature (`aircrack-ng` integration) is meant strictly for networks you own or have explicit permission to test. Testing networks without authorization is illegal in most jurisdictions.
