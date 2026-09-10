import sqlite3
import pandas as pd

def connector(path: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    return con,cur

def create_table(con: sqlite3.Connection, cur: sqlite3.Cursor):
    cur.execute("""CREATE TABLE IF NOT EXISTS AP(
    BSSID TEXT PRIMARY KEY,
    SSID TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS scan(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    BSSID TEXT,
    IN_USE TEXT,
    CHAN INTEGER,
    FREQ INTEGER,
    SIGNAL INTEGER,
    BARS TEXT,
    SECURITY TEXT,
    LATITUDE REAL,
    LONGITUDE REAL,
    RISK1 INTEGER,
    RISK2 INTEGER,
    RISK3 INTEGER,
    TOTAL_RISK INTEGER,
    EVIL TEXT,
    TIMESTAMP TEXT,
    FOREIGN KEY (BSSID) REFERENCES AP(BSSID)
    )""")
    con.commit()

def insert_items(con: sqlite3.Connection, cur: sqlite3.Cursor, wifi: pd.DataFrame, latitude: float, longitude: float, now: str):
    for i in range(len(wifi)):
        bssid = wifi.loc[i, 'BSSID']
        ssid = wifi.loc[i, 'SSID']

        cur.execute("INSERT OR IGNORE INTO AP (BSSID, SSID) VALUES (?,?)", (bssid, ssid))
        cur.execute("""
            INSERT INTO scan (
                BSSID, IN_USE, CHAN, FREQ, SIGNAL, BARS, SECURITY,
                LATITUDE, LONGITUDE, RISK1, RISK2, RISK3, TOTAL_RISK, EVIL, TIMESTAMP
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bssid,
            str(wifi.loc[i, 'IN-USE']),
            int(wifi.loc[i, 'CHAN']),
            int(wifi.loc[i, 'FREQ']),
            int(wifi.loc[i, 'SIGNAL']),
            str(wifi.loc[i, 'BARS']),
            str(wifi.loc[i, 'SECURITY']),
            latitude,
            longitude,
            int(wifi.loc[i, 'RISK 1']),
            int(wifi.loc[i, 'RISK 2']),
            int(wifi.loc[i, 'RISK 3']),
            int(wifi.loc[i, 'TOTAL RISK']),
            str(wifi.loc[i, 'EVIL']),
            now
        ))
    con.commit()

def get_duplicate_bssid(cur: sqlite3.Cursor, ssid: str) -> list:
    cur.execute("SELECT BSSID FROM AP WHERE SSID = ?", (ssid,))
    found_bssids = [row[0] for row in cur.fetchall()]
    return found_bssids

def get_last_seen(cur: sqlite3.Cursor, ssid: str, exclude_bssid: str) -> tuple:
    cur.execute("""
        SELECT scan.LATITUDE, scan.LONGITUDE, scan.TIMESTAMP
        FROM scan
        JOIN AP ON scan.BSSID = AP.BSSID
        WHERE AP.SSID = ? AND scan.BSSID != ?
        ORDER BY scan.TIMESTAMP DESC
        LIMIT 1
    """, (ssid, exclude_bssid))
    return cur.fetchone()

def close_connection(con: sqlite3.Connection):
    con.close()