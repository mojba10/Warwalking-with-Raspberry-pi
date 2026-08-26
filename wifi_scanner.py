import subprocess
import re

def sacnning(IFACE:str) -> str:
    wifi_str = subprocess.getoutput(f"nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,BARS,SECURITY device wifi list ifname {IFACE}")
    return wifi_str

def sep_rows(wifi_str:str) -> list:
    rows = []
    for line in wifi_str.strip().split("\n"):
        rows.append(line)
    return rows
# using loop for seprate each AP

class wifi():
    def __init__(self, wifi):
        parts = re.split(r"(?<!\\):", wifi)
        if len(parts) == 8:
            self.IN-USE = parts[0]
            self.BSSID = parts[1].replace("\\:",":")
            self.SSID = parts[2]
            self.CHAN = int(parts[3]) if parts[3].strip().isdigit() else None
            self.FREQ = int(parts[4].replace("MHz", "").strip()) if parts[4].replace("MHz", "").strip().isdigit() else None
            self.SIGNAL = int(parts[5]) if parts[5].strip().isdigit() else None
            self.BARS = parts[6]
            self.SECURITY = parts[7] if parts[7].strip() else "OPEN"