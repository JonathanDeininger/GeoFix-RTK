import socket
import time
import csv
import datetime
import os

def nmea_to_decimal(coord, direction):
    try:
        if len(coord.split('.')[0]) > 4:
            degrees = int(coord[:3])
            minutes = float(coord[3:])
        else:
            degrees = int(coord[:2])
            minutes = float(coord[2:])
        decimal = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal *= -1
        return round(decimal, 7)
    except Exception as e:
        print(f"Fehler bei Umrechnung: {e}")
        return None

def interpret_fix_status(code):
    return {
        '0': 'Kein Fix', # No Fix
        '1': '2D/3D Fix', # 2D/3D Fix - does not use the base station
        '2': 'DGNSS', # uses the base station but not RTK
        '4': 'RTK Fix', # uses the base station and RTK
        '5': 'RTK Float', # uses the base station and RTK but with reduced accuracy
        '6': 'Dead Reckoning', # Dead Reckoning
    }.get(code, 'Unbekannt')

# Konfiguration
TCP_IP = '10.42.0.30'
TCP_PORT = 33
BUFFER_SIZE = 1024

# CSV-Datei erstellen
csv_filename = f"gps_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_filepath = os.path.join(os.path.dirname(__file__), csv_filename)

# CSV-Header schreiben
with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Fix_Status', 'Fix_Description'])

print(f"📝 CSV-Log wird gespeichert in: {csv_filepath}")
print("🔁 Starte GNSS-Client mit automatischer Wiederverbindung...")

while True:
    try:
        with socket.create_connection((TCP_IP, TCP_PORT), timeout=10) as s:
            print("✅ Verbindung erfolgreich. Warte auf NMEA-Daten...")

            while True:
                data = s.recv(BUFFER_SIZE).decode(errors='ignore')

                if not data:
                    raise ConnectionError("Keine Daten empfangen")

                for line in data.splitlines():
                    if "$GNGGA" in line or "$GPGGA" in line:
                        fields = line.split(',')

                        if len(fields) < 7:
                            continue

                        lat_raw = fields[2]
                        lat_dir = fields[3]
                        lon_raw = fields[4]
                        lon_dir = fields[5]
                        fix_status = fields[6]

                        lat = nmea_to_decimal(lat_raw, lat_dir)
                        lon = nmea_to_decimal(lon_raw, lon_dir)
                        fix_desc = interpret_fix_status(fix_status)

                        if lat is not None and lon is not None:
                            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            # In CSV schreiben
                            with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow([timestamp, lat, lon, fix_status, fix_desc])
                            
                            print(f"🌍 Position: {lat}, {lon} | 📡 Fix: {fix_desc}")
                                
    except Exception as e:
        print(f"⚠️  Verbindung verloren oder fehlgeschlagen: {e}")
        print("⏳ Neuer Verbindungsversuch in 2 Sekunden...")
        time.sleep(2)

