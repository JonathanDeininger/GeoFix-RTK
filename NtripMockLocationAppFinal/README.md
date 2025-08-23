# NtripMockLocationAppFinal

Eine Android-App zum Empfangen von GNSS-Koordinaten (z.B. RTK/GeoFix) über eine TCP-Verbindung (NTRIP-ähnlich) und zum Setzen von Mock Locations auf dem Gerät. Zusätzlich können empfangene Positionsdaten als CSV-Log gespeichert werden.

## Hauptfunktionen

- Verbindung zu einem NTRIP-ähnlichen TCP-Server (IP/Port einstellbar)
- Empfangen und Parsen von GGA-NMEA-Datensätzen
- Setzen von Mock Locations (GPS/Netzwerk) auf dem Gerät
- Anzeige von Positionsdaten, RTK-Status, Satellitenzahl, HDOP, Geoid-Höhe etc.
- CSV-Logging der empfangenen GeoFix-Daten (optional)
- Hinweise zu aktiven echten Providern (z.B. GPS/Netzwerk)
- Automatische Wiederverbindung bei Verbindungsabbruch

## Voraussetzungen

- Android-Gerät mit Entwickleroptionen und aktivierter "Mock Location App" (diese App auswählen)
- Standort- und Schreibrechte (werden beim Start abgefragt)
- Ein NTRIP-ähnlicher Server, der GGA-NMEA-Datensätze über TCP bereitstellt

## Nutzung

1. **App installieren** und als "Mock Location App" in den Entwickleroptionen auswählen.
2. **App starten**. Die App prüft, ob echte Standort-Provider aktiv sind und gibt Hinweise.
3. **IP-Adresse und Port** des NTRIP-Servers eingeben.
4. Optional: **CSV-Logging** per Schalter aktivieren.
5. **"Verbinden"** drücken. Die App verbindet sich, zeigt Status und Positionsdaten an und setzt Mock Locations.
6. **"Verbindung trennen"** beendet die Verbindung und das Logging.

## Hinweise

- Für beste Ergebnisse sollten echte Standortdienste (GPS/Netzwerk) deaktiviert werden (Flugmodus empfohlen).
- CSV-Logs werden im **Downloads**-Verzeichnis gespeichert.
- Die App benötigt **Standort- und Schreibrechte**.
- Die App ist für Test- und Entwicklungszwecke gedacht.

## Felder im CSV-Log

- Timestamp
- Latitude, Longitude, Altitude
- RTK_Quality, Fix_Type
- Satellites, HDOP, Quality_Assessment
- Geoid_Height, DGPS_ID
- Raw_NMEA

## Lizenz

Nur für Forschungs- und Lehrzwecke. Keine Garantie oder Haftung.
