from flask import Flask, render_template, jsonify
import sqlite3
from core.config import DB_PATH

app = Flask(__name__)

current_scan = None

def set_current_scan(wifi):
    global current_scan
    current_scan = wifi

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/api/current')
def api_current():
    if current_scan is None:
        return jsonify([])
    
    rows = []
    for i in range(len(current_scan)):
        rows.append({
            'id': i,
            'BSSID': current_scan.loc[i, 'BSSID'],
            'SSID': current_scan.loc[i, 'SSID'],
            'CHAN': int(current_scan.loc[i, 'CHAN']) if current_scan.loc[i, 'CHAN'] is not None else None,
            'SIGNAL': int(current_scan.loc[i, 'SIGNAL']) if current_scan.loc[i, 'SIGNAL'] is not None else None,
            'SECURITY': current_scan.loc[i, 'SECURITY'],
            'LATITUDE': float(current_scan.loc[i, 'LATITUDE']) if 'LATITUDE' in current_scan.columns else None,
            'LONGITUDE': float(current_scan.loc[i, 'LONGITUDE']) if 'LONGITUDE' in current_scan.columns else None,
            'TOTAL_RISK': int(current_scan.loc[i, 'TOTAL RISK']),
            'EVIL': current_scan.loc[i, 'EVIL'],
            'TIMESTAMP': current_scan.loc[i, 'TIMESTAMP']
        })

    return jsonify(rows)

@app.route('/api/history')
def api_history():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT scan.id, AP.BSSID, AP.SSID, scan.CHAN, scan.SIGNAL,
               scan.SECURITY, scan.LATITUDE, scan.LONGITUDE,
               scan.TOTAL_RISK, scan.EVIL, scan.TIMESTAMP
        FROM scan
        JOIN AP ON scan.BSSID = AP.BSSID
        ORDER BY scan.TIMESTAMP DESC
    """)
    rows = []
    for row in cur.fetchall():
        row_dict = dict(row)
        rows.append(row_dict)
    con.close()
    return jsonify(rows)