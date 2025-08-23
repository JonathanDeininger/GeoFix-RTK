# GeoFix-RTK & Tools

Dieses Repository enthält eine Android-App zur Mock-Location-Simulation mit RTK/GNSS-Daten sowie verschiedene Python-Skripte zur Auswertung und Weiterverarbeitung der Positionsdaten.

---

## 📱 NtripMockLocationAppFinal (Android-App)

Eine Android-App zum Empfangen von GNSS-Koordinaten (z.B. RTK/GeoFix) über eine TCP-Verbindung (NTRIP-ähnlich) und zum Setzen von Mock Locations auf dem Gerät. Zusätzlich können empfangene Positionsdaten als CSV-Log gespeichert werden.

### Hauptfunktionen

- Verbindung zu einem NTRIP-ähnlichen TCP-Server (IP/Port einstellbar)
- Empfangen und Parsen von GGA-NMEA-Datensätzen
- Setzen von Mock Locations (GPS/Netzwerk) auf dem Gerät
- Anzeige von Positionsdaten, RTK-Status, Satellitenzahl, HDOP, Geoid-Höhe etc.
- CSV-Logging der empfangenen GeoFix-Daten (optional)
- Hinweise zu aktiven echten Providern (z.B. GPS/Netzwerk)
- Automatische Wiederverbindung bei Verbindungsabbruch

### Voraussetzungen

- Android-Gerät mit Entwickleroptionen und aktivierter "Mock Location App" (diese App auswählen)
- Standort- und Schreibrechte (werden beim Start abgefragt)
- Ein NTRIP-ähnlicher Server, der GGA-NMEA-Datensätze über TCP bereitstellt

### Nutzung

1. **App installieren** und als "Mock Location App" in den Entwickleroptionen auswählen.
2. **App starten**. Die App prüft, ob echte Standort-Provider aktiv sind und gibt Hinweise.
3. **IP-Adresse und Port** des NTRIP-Servers eingeben.
4. Optional: **CSV-Logging** per Schalter aktivieren.
5. **"Verbinden"** drücken. Die App verbindet sich, zeigt Status und Positionsdaten an und setzt Mock Locations.
6. **"Verbindung trennen"** beendet die Verbindung und das Logging.

### Hinweise

- Für beste Ergebnisse sollten echte Standortdienste (GPS/Netzwerk) deaktiviert werden (Flugmodus empfohlen).
- CSV-Logs werden im **Downloads**-Verzeichnis gespeichert.
- Die App benötigt **Standort- und Schreibrechte**.
- Die App ist für Test- und Entwicklungszwecke gedacht.

### Felder im CSV-Log

- Timestamp
- Latitude, Longitude, Altitude
- RTK_Quality, Fix_Type
- Satellites, HDOP, Quality_Assessment
- Geoid_Height, DGPS_ID
- Raw_NMEA

---

## 🐍 Python-Skripte

### 1. `receive_gps_location_rover.py`

Empfängt GNSS-Daten (NMEA GGA) von einem TCP-Server, wandelt sie in Dezimalgrad um und speichert sie mit Fix-Status in eine CSV-Datei.

**Features:**
- Automatische Wiederverbindung bei Verbindungsabbruch
- CSV-Logging mit Zeitstempel, Koordinaten und Fix-Status
- Konsolenausgabe der aktuellen Position

**Nutzung:**
- Passe `TCP_IP` und `TCP_PORT` an deinen Server an.
- Starte das Skript:  
  `python receive_gps_location_rover.py`
- Die CSV-Datei wird im gleichen Verzeichnis gespeichert.

---

### 2. `extract_coordinates.py`

Extrahiert gültige Koordinatenpaare aus einer GPS-Log-CSV (z.B. aus `receive_gps_location_rover.py`) und speichert sie in eine neue CSV-Datei.

**Features:**
- Filtert nur Zeilen mit gültigem Fix-Status
- Entfernt Duplikate
- Ausgabe: `gpslog_coordinates.csv`

**Nutzung:**
- Lege die zu verarbeitende CSV als `gpslog.csv` ins Verzeichnis.
- Starte das Skript:  
  `python extract_coordinates.py`

---

### 3. `csv_to_kml.py`

Konvertiert eine Koordinaten-CSV (`gpslog_coordinates.csv`) in eine KML-Datei für Google Earth/Maps.

**Features:**
- Erstellt eine KML mit Pfad (Track) und optional Einzelpunkten
- KML kann in Google Earth, Google Maps oder GIS-Tools geöffnet werden

**Nutzung:**
- Stelle sicher, dass `gpslog_coordinates.csv` vorhanden ist.
- Starte das Skript:  
  `python csv_to_kml.py`

---

### 4. `auswertung_screenshots.py`

Extrahiert Messwerte (meanAcc, siv, sip, pdop) aus Screenshots mittels OCR (Tesseract) und erstellt eine Auswertungs-CSV.

**Features:**
- OCR-Analyse von Screenshots mit Tesseract
- Extrahiert Werte und Zeitstempel aus Dateinamen/Text
- Erstellt CSV mit Zeitverlauf und Messwerten

**Nutzung:**
- Installiere Tesseract und passe ggf. den Pfad in der Datei an.
- Lege die Screenshots im gewünschten Verzeichnis ab.
- Passe `screenshots_path` im Skript an.
- Starte das Skript:  
  `python auswertung_screenshots.py`

---

## Lizenz

Nur für Forschungs- und Lehrzwecke. Keine Garantie oder Haftung.
