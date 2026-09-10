from core import wifi_scanner, gps_reader, security_analyzer, evil_twin_detector
from core.config import IFACE, DB_PATH
from web import app as webapp
from database import db_manager
import subprocess
import datetime

subprocess.getoutput('sudo pinctrl set 14 a5')
subprocess.getoutput('sudo pinctrl set 15 a5')

print("Scanning...")
wifi = wifi_scanner.scanning()
now = str(datetime.datetime.now())

print("Locating...")
location = gps_reader.read_gps()
lat = location['latitude'] if location else None
lon = location['longitude'] if location else None

print("Analyzing...")
wifi = security_analyzer.risk_standard(wifi)
wifi = security_analyzer.risk_default(wifi)
subprocess.getoutput(f'sudo nmcli device set {IFACE} managed no')
subprocess.getoutput(f"sudo airmon-ng start {IFACE}")
try:
    wifi = security_analyzer.risk_password(wifi)
finally:
    subprocess.getoutput(f'sudo nmcli device set {IFACE} managed yes')
wifi = security_analyzer.total_risk(wifi)

print("Creating Database...")
con, cur = db_manager.connector(DB_PATH)
db_manager.create_table(con, cur)

print("Finding Evil...")
wifi, ess = evil_twin_detector.check_evil_current(wifi)
wifi = evil_twin_detector.check_evil_history(wifi, cur, lat, lon, ess)

wifi['LATITUDE'] = lat
wifi['LONGITUDE'] = lon
wifi['TIMESTAMP'] = now

print("completing Database...")
db_manager.insert_items(con, cur, wifi, lat, lon, now)
db_manager.close_connection(con)

webapp.set_current_scan(wifi)
webapp.app.run(host='0.0.0.0', debug=True, use_reloader=False)