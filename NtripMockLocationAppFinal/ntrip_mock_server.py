#!/usr/bin/env python3
"""
NTRIP Mock Server für Android App Testing
Simuliert NMEA GPS-Daten über TCP Socket
"""

import socket
import time
import threading
import random
from datetime import datetime

class NTRIPMockServer:
    def __init__(self, host='0.0.0.0', port=33):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        
        # Startposition (München als Beispiel)
        self.base_lat = 48.1351
        self.base_lon = 11.5820
        
        # Bewegungsparameter
        self.movement_range = 0.001  # ~100m Radius
        self.update_interval = 0.5   # Häufigere Updates (alle 0.5 Sekunden)

    def start_server(self):
        """Startet den Mock NTRIP Server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 NTRIP Mock Server gestartet auf {self.host}:{self.port}")
            print(f"📍 Basis-Position: {self.base_lat:.6f}, {self.base_lon:.6f}")
            print("🔄 Warte auf Verbindungen...")
            
            # Thread für GPS-Daten-Generation
            gps_thread = threading.Thread(target=self.generate_gps_data)
            gps_thread.daemon = True
            gps_thread.start()
            
            # Hauptloop für Client-Verbindungen
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"✅ Client verbunden: {address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("❌ Socket Fehler")
                    break
                    
        except Exception as e:
            print(f"❌ Server Fehler: {e}")
        finally:
            self.stop_server()

    def handle_client(self, client_socket, address):
        """Behandelt einzelne Client-Verbindung"""
        self.clients.append(client_socket)
        try:
            while self.running:
                # Keep-alive
                time.sleep(1)
        except Exception as e:
            print(f"❌ Client {address} Fehler: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"❌ Client getrennt: {address}")

    def generate_gps_data(self):
        """Generiert und sendet kontinuierlich GPS-Daten"""
        while self.running:
            try:
                # Simuliere leichte Bewegung um Basis-Position
                lat_offset = random.uniform(-self.movement_range, self.movement_range)
                lon_offset = random.uniform(-self.movement_range, self.movement_range)
                
                current_lat = self.base_lat + lat_offset
                current_lon = self.base_lon + lon_offset
                
                # Erstelle NMEA GNGGA Nachricht
                nmea_sentence = self.create_gngga_sentence(current_lat, current_lon)
                
                # GNSS Details aus der generierten Nachricht extrahieren
                fields = nmea_sentence.split(",")
                fix_quality = fields[6] if len(fields) > 6 else "1"
                satellites = fields[7] if len(fields) > 7 else "0"
                hdop = fields[8] if len(fields) > 8 else "0.0"
                
                fix_type_map = {
                    "1": "GPS",
                    "2": "DGPS", 
                    "4": "RTK Fixed",
                    "5": "RTK Float"
                }
                fix_type = fix_type_map.get(fix_quality, "GPS")
                
                # Sende an alle verbundenen Clients
                if self.clients:
                    print(f"📡 GPS: {current_lat:.6f}, {current_lon:.6f} | {fix_type} | {satellites} Sats | HDOP: {hdop}")
                    disconnected_clients = []
                    
                    for client in self.clients:
                        try:
                            client.send((nmea_sentence + '\r\n').encode('utf-8'))
                        except:
                            disconnected_clients.append(client)
                    
                    # Entferne getrennte Clients
                    for client in disconnected_clients:
                        if client in self.clients:
                            self.clients.remove(client)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ GPS Generation Fehler: {e}")
                time.sleep(1)

    def create_gngga_sentence(self, lat, lon):
        """Erstellt eine NMEA GNGGA Sentence mit realistischen GNSS-Daten"""
        # Zeit im HHMMSS Format
        now = datetime.utcnow()
        time_str = now.strftime("%H%M%S.00")
        
        # Latitude Konvertierung
        lat_deg = int(abs(lat))
        lat_min = (abs(lat) - lat_deg) * 60
        lat_str = f"{lat_deg:02d}{lat_min:07.4f}"
        lat_dir = "N" if lat >= 0 else "S"
        
        # Longitude Konvertierung  
        lon_deg = int(abs(lon))
        lon_min = (abs(lon) - lon_deg) * 60
        lon_str = f"{lon_deg:03d}{lon_min:07.4f}"
        lon_dir = "E" if lon >= 0 else "W"
        
        # RTK Fix Quality simulieren (gewichtete Auswahl für realistischere Simulation)
        fix_qualities = ["1", "1", "2", "2", "4", "5"]  # Mehr GPS/DGPS, weniger RTK
        fix_quality = random.choice(fix_qualities)
        
        # Anzahl der Satelliten (abhängig von Fix Quality)
        if fix_quality in ["4", "5"]:  # RTK
            satellites = f"{random.randint(10, 16):02d}"
        elif fix_quality == "2":  # DGPS
            satellites = f"{random.randint(8, 12):02d}"
        else:  # GPS
            satellites = f"{random.randint(6, 10):02d}"
        
        # HDOP - Horizontal Dilution of Precision (abhängig von Fix Quality)
        if fix_quality in ["4", "5"]:  # RTK - sehr gute Präzision
            hdop = f"{random.uniform(0.5, 1.2):.1f}"
        elif fix_quality == "2":  # DGPS - gute Präzision
            hdop = f"{random.uniform(0.8, 2.0):.1f}"
        else:  # GPS - normale Präzision
            hdop = f"{random.uniform(1.5, 4.0):.1f}"
        
        # Höhe über Meeresspiegel (München ca. 520m + Variation)
        altitude = f"{random.uniform(515.0, 550.0):.1f}"
        
        # Geoid-Höhe (für München ca. 47m)
        geoid_height = f"{random.uniform(46.0, 48.0):.1f}"
        
        # DGPS Alter (nur für DGPS/RTK relevant)
        dgps_age = ""
        dgps_id = ""
        if fix_quality in ["2", "4", "5"]:
            dgps_age = f"{random.uniform(1.0, 15.0):.1f}"
            dgps_id = f"{random.randint(1000, 1999)}"
        
        # GNGGA Sentence aufbauen
        sentence = f"$GNGGA,{time_str},{lat_str},{lat_dir},{lon_str},{lon_dir},{fix_quality},{satellites},{hdop},{altitude},M,{geoid_height},M,{dgps_age},{dgps_id}"
        
        # Checksum berechnen
        checksum = 0
        for char in sentence[1:]:  # Skip das '$'
            checksum ^= ord(char)
        
        return f"{sentence}*{checksum:02X}"

    def stop_server(self):
        """Stoppt den Server"""
        print("\n🛑 Server wird gestoppt...")
        self.running = False
        
        # Schließe alle Client-Verbindungen
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        # Schließe Server Socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("✅ Server gestoppt")

def main():
    """Hauptfunktion"""
    print("=" * 50)
    print("🛰️  NTRIP Mock Server für Android App Test")
    print("=" * 50)
    
    # Konfiguration
    HOST = '0.0.0.0'  # Alle Interfaces
    PORT = 33         # Standard NTRIP Port
    
    server = NTRIPMockServer(HOST, PORT)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n⚠️  Strg+C erkannt")
    finally:
        server.stop_server()

if __name__ == "__main__":
    main()
