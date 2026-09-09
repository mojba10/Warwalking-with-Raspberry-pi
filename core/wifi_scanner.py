from core.config import IFACE
import re
import pandas as pd
import subprocess

def scanning() -> pd.DataFrame:
    wifi_str = subprocess.getoutput(f"nmcli -t -f IN-USE,BSSID,SSID,CHAN,FREQ,SIGNAL,BARS,SECURITY device wifi list ifname {IFACE}")
    rows = []
    for line in wifi_str.strip().split("\n"):
        parts = re.split(r"(?<!\\):",line)
        if len(parts) == 8:
            rows.append({
            "IN-USE": parts[0],
            "BSSID": parts[1].replace("\\:",":"),
            "SSID": parts[2],
            "CHAN": int(parts[3]) if parts[3].strip().isdigit() else None,
            "FREQ": int(parts[4].replace("MHz","").strip()) if parts[4].replace("MHz", "").strip().isdigit() else None,
            "SIGNAL": int(parts[5]) if parts[5].strip().isdigit() else None,
            "BARS": parts[6],
            "SECURITY": parts[7] if parts[7].strip() else "OPEN"
            })
    
    wifi_table = pd.DataFrame(rows)
    return wifi_table