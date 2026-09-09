import math
import pandas as pd
import sqlite3
from datetime import datetime
from database import db_manager


def same_ssid(wifi: pd.DataFrame) -> list:
    ssid = list(wifi['SSID'])
    unique_ssid = set(ssid)
    return [item for item in unique_ssid if ssid.count(item) > 1 and item != '']


def check_novelty(wifi: pd.DataFrame, cur: sqlite3.Cursor) -> list:
    duplicates = set()
    for i in range(len(wifi)):
        ssid = wifi.loc[i, 'SSID']
        bssid = wifi.loc[i, 'BSSID']
        if ssid == '':
            continue
        found_bssids = db_manager.get_duplicate_bssid(cur, ssid)
        if any(b != bssid for b in found_bssids):
            duplicates.add(ssid)
    return list(duplicates)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def check_evil_current(wifi: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    if 'EVIL' not in wifi.columns:
        wifi['EVIL'] = 'NONE'

    dup = same_ssid(wifi)
    ess = set()
    for name in dup:
        indices = list(wifi[wifi["SSID"] == name].index)
        for i in indices:
            for j in indices:
                if i == j:
                    continue
                security_dif = wifi.loc[i, 'SECURITY'] != wifi.loc[j, 'SECURITY']
                brand_dif = wifi.loc[i, "BSSID"][:8] != wifi.loc[j, "BSSID"][:8]
                if security_dif and brand_dif:
                    wifi.loc[i, 'EVIL'] = 'MEDIUM'
                    wifi.loc[j, 'EVIL'] = 'MEDIUM'

        if len(indices) > 2:
            ouis = set(wifi.loc[idx, "BSSID"][:8] for idx in indices)
            if len(ouis) == 1:  
                ess.add(name)

    return wifi, ess


def check_evil_history(wifi: pd.DataFrame, cur: sqlite3.Cursor, latitude: float, longitude: float, ess: set, max_distance_km=1.0, max_hours=48) -> pd.DataFrame:
    if 'EVIL' not in wifi.columns:
        wifi['EVIL'] = 'NONE'

    novel_ssids = check_novelty(wifi, cur)

    for i in range(len(wifi)):
        ssid = wifi.loc[i, 'SSID']
        bssid = wifi.loc[i, 'BSSID']

        if ssid not in novel_ssids or latitude is None or longitude is None:
            continue

        if ssid in ess:
            wifi.loc[i, "EVIL"] = 'NONE'
            continue

        last_seen = db_manager.get_last_seen(cur, ssid, bssid)
        if not last_seen:
            new_level = 'LOW'
        else:
            last_lat, last_lon, last_time = last_seen
            near = False
            recent = False

            if last_lat is not None and last_lon is not None:
                distance = haversine(latitude, longitude, last_lat, last_lon)
                near = distance <= max_distance_km

            if last_time is not None:
                last_dt = datetime.fromisoformat(last_time)
                hours_diff = abs((datetime.now() - last_dt).total_seconds()) / 3600
                recent = hours_diff <= max_hours

            if near and recent:
                new_level = 'HIGH'
            elif near or recent:
                new_level = 'MEDIUM'
            else:
                new_level = 'LOW'

        levels = {'NONE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        if levels[new_level] > levels[wifi.loc[i, 'EVIL']]:
            wifi.loc[i, 'EVIL'] = new_level

    return wifi