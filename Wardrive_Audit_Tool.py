import csv, sys, os, urllib.request, json, re, time, itertools
from datetime import datetime
import math

class Color:
    BLUE = '\033[94m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    RED = '\033[91m'; CYAN = '\033[96m'; BOLD = '\033[1m'; END = '\033[0m'
    CLEAR = '\033[K'

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius der Erde in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_oui_dict():
    cache_file = "oui_database.txt"
    if not os.path.exists(cache_file):
        try:
            url = "https://standards-oui.ieee.org/oui/oui.txt"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                data = res.read().decode('utf-8', errors='ignore')
                with open(cache_file, "w", encoding="utf-8") as f: f.write(data)
        except: return {}
    with open(cache_file, "r", encoding="utf-8") as f:
        data = f.read()
    return {m[0].replace('-', '').upper(): m[1].strip() for m in re.findall(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', data)}

def get_city_live(lat, lon, zoom):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom={zoom}"
        req = urllib.request.Request(url, headers={'User-Agent': 'EliteAudit/18.0'})
        time.sleep(1.2) 
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            addr = data.get('address', {})
            return addr.get('city') or addr.get('town') or addr.get('village') or addr.get('county') or "Unknown Region"
    except: return f"Loc {lat}/{lon}"

def run_master_audit(file_path):
    os.system('clear')
    print(f"{Color.BOLD}{Color.CYAN}┌──────────────────────────────────────────────────────────┐")
    print(f"│             WARDRIVE AUDIT TOOL                   │")
    print(f"└──────────────────────────────────────────────────────────┘{Color.END}")
    
    print(f"\n{Color.BOLD}SELECT PRECISION:{Color.END}")
    print(" [1] Turbo Mode (5km - Fast)")
    print(" [2] Detail Mode (500m - In-depth)")
    mode = input("\n Select (1/2): ")
    precision = 1 if mode == '1' else 2
    geo_zoom = 10 if mode == '1' else 14

    stats = {
        'total': 0, 'wifi': 0, 'ble': 0, 'cell': 0, 'bt': 0,
        'geo_raw': {}, 'vendors': {}, 'channels': {},
        'sec': {'WPA3':0, 'WPA2':0, 'WPA':0, 'WEP':0, 'Open':0, 'WPS':0},
        'coords': [], 'first_ts': None, 'last_ts': None
    }
    
    start_processing_time = datetime.now()
    
    with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        f.readline()
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if i % 1000 == 0:
                sys.stdout.write(f"\r{Color.CLEAR}{Color.YELLOW} 🛰️  LIVE FEED: WiFi:{stats['wifi']} | Cell:{stats['cell']} | BLE:{stats['ble']} | Rows:{i}{Color.END}")
                sys.stdout.flush()
            
            stats['total'] += 1
            rtype = row.get('Type', '')
            
            # Zeit erfassen für Punkt 5
            row_ts = row.get('FirstSeen', '')
            if row_ts:
                if not stats['first_ts']: stats['first_ts'] = row_ts
                stats['last_ts'] = row_ts

            lat, lon = float(row.get('CurrentLatitude', 0)), float(row.get('CurrentLongitude', 0))
            if lat != 0:
                stats['coords'].append((lat, lon))
                k = (round(lat, precision), round(lon, precision))
                stats['geo_raw'][k] = stats['geo_raw'].get(k, 0) + 1

            if rtype == 'WIFI':
                stats['wifi'] += 1
                auth = row.get('AuthMode', '')
                if 'WPA3' in auth or 'SAE' in auth: stats['sec']['WPA3'] += 1
                elif 'WPA2' in auth: stats['sec']['WPA2'] += 1
                elif 'WEP' in auth: stats['sec']['WEP'] += 1
                if '[WPS]' in auth: stats['sec']['WPS'] += 1
                if not any(x in auth for x in ['WPA', 'WEP', 'PSK']): stats['sec']['Open'] += 1
                
                ch = row.get('Channel', '0')
                stats['channels'][ch] = stats['channels'].get(ch, 0) + 1
                mac = row.get('MAC', '').replace(':', '').upper()[:6]
                stats['vendors'][mac] = stats['vendors'].get(mac, 0) + 1
            
            elif rtype == 'BLE': stats['ble'] += 1
            elif rtype == 'BT': stats['bt'] += 1
            elif rtype in ['GSM', 'LTE', 'NR', 'CDMA']: stats['cell'] += 1

    # Distanz-Berechnung
    total_dist = 0
    if len(stats['coords']) > 1:
        for j in range(len(stats['coords']) - 1):
            total_dist += calculate_distance(stats['coords'][j][0], stats['coords'][j][1], stats['coords'][j+1][0], stats['coords'][j+1][1])

    print(f"\n\n{Color.GREEN}[✓] Analysis Complete. Total Distance: {total_dist:.2f} km{Color.END}")
    confirm = input(f"{Color.YELLOW}Generate Advanced Report? (y/n): {Color.END}").lower()
    if confirm != 'y': return

    # OUI Aggregation
    oui_db = get_oui_dict()
    aggregated_vendors = {}
    for oui, count in stats['vendors'].items():
        brand = oui_db.get(oui, "Unknown").split()[0].replace(',', '').strip()
        aggregated_vendors[brand] = aggregated_vendors.get(brand, 0) + count

    # Geo Mapping
    final_cities = {}
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    try:
        for (lat, lon), count in stats['geo_raw'].items():
            sys.stdout.write(f"\r{Color.CLEAR}{Color.YELLOW}[{next(spinner)}] Mapping Regions: {lat}, {lon}{Color.END}")
            sys.stdout.flush()
            city = get_city_live(lat, lon, geo_zoom)
            final_cities[city] = final_cities.get(city, 0) + count
    except KeyboardInterrupt: pass

    # Report Erstellung
    ts_file = datetime.now().strftime("%Y%m%d_%H%M")
    fn = f"Wardriving_Audit_{ts_file}.md"
    
    with open(fn, 'w', encoding='utf-8') as md:
        md.write(f"# 🛡️ PROFESSIONAL WARDRIVING INFRASTRUCTURE AUDIT\n\n")
        
        md.write("## 1. Geographical Summary\n| Region | Signals | Share |\n| :--- | :--- | :--- |\n")
        for c, count in sorted(final_cities.items(), key=lambda x: x[1], reverse=True):
            md.write(f"| {c} | {count} | {(count/stats['total']*100):.1f}% |\n")

        md.write("\n## 2. Vendor Market Share\n| Brand | Count | WiFi Share |\n| :--- | :--- | :--- |\n")
        for name, count in sorted(aggregated_vendors.items(), key=lambda x: x[1], reverse=True)[:30]:
            md.write(f"| {name} | {count} | {(count/stats['wifi']*100):.1f}% |\n")

        md.write("\n## 3. Security Risk & Network Deep-Dive\n")
        md.write("### Encryption Table\n| Protocol | Count | Percentage |\n| :--- | :--- | :--- |\n")
        for k, v in stats['sec'].items():
            if k != 'WPS': md.write(f"| {k} | {v} | {(v/stats['wifi']*100):.1f}% |\n")
        
        md.write(f"\n### Critical Vulnerabilities\n- **WPS Enabled:** {stats['sec']['WPS']}\n")
        md.write(f"- **Open Networks:** {stats['sec']['Open']}\n")
        md.write(f"- **WEP Legacy:** {stats['sec']['WEP']}\n\n")
        
        md.write("### Channel Load Analysis\n| Channel | APs | Status |\n| :--- | :--- | :--- |\n")
        for ch, count in sorted(stats['channels'].items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)[:15]:
            load = "🔴 High" if count > (stats['wifi']*0.08) else "🟢 Low"
            md.write(f"| Ch {ch} | {count} | {load} |\n")

        md.write("\n## 4. Other Wireless Intelligence\n")
        md.write(f"- Cellular Nodes: {stats['cell']}\n")
        md.write(f"- BLE Trackers/Devices: {stats['ble']}\n")
        md.write(f"- Bluetooth Classic: {stats['bt']}\n")

        md.write("\n## 5. About this Run\n")
        md.write(f"- **Run Start:** {stats['first_ts']}\n")
        md.write(f"- **Run End:** {stats['last_ts']}\n")
        md.write(f"- **Total Distance:** {total_dist:.2f} km\n")
        md.write(f"- **Data Nodes Scanned:** {stats['total']}\n")
        md.write(f"- **Audit File:** {os.path.basename(file_path)}\n")

    print(f"\n\n{Color.GREEN}{Color.BOLD}[✓] REPORT GENERATED: {fn}{Color.END}")

if __name__ == "__main__":
    if len(sys.argv) > 1: run_master_audit(sys.argv[1])