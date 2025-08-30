from PIL import Image
import pytesseract
import os
import re
import pandas as pd
from datetime import datetime

# Falls Tesseract nicht im PATH ist, hier den Pfad zur ausführbaren Datei angeben:
# Beispiel für Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Pfad zum Screenshots-Verzeichnis (wird in main überschrieben)
screenshots_path = r'./'

def extract_meanAcc_from_text(text):
    """
    Extrahiert den Wert nach 'meanAcc=' aus dem Text
    """
    pattern = r'meanAcc=(\d+(?:\.\d+)?)'
    match = re.search(pattern, text)
    if match:
        return float(match.group(1))
    return None

def extract_siv_from_text(text):
    """
    Extrahiert den Wert nach 'siv:' aus dem Text
    """
    pattern = r'siv:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_sip_from_text(text):
    """
    Extrahiert den Wert nach 'sip:' aus dem Text
    """
    pattern = r'sip:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_pdop_from_text(text):
    """
    Extrahiert den Wert nach 'pdop:' aus dem Text
    """
    pattern = r'pdop:\s*(\d+(?:\.\d+)?)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def extract_timestamp_from_filename(filename):
    """
    Extrahiert Timestamp aus dem Dateinamen
    Format: screenshot_2025-07-10_18-15-00.png
    """
    pattern = r'screenshot_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})\.png'
    match = re.search(pattern, filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2).replace('-', ':')
        datetime_str = f"{date_str} {time_str}"
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    return None

def process_screenshots(path=None):
    """
    Verarbeitet alle Screenshots im Verzeichnis und extrahiert meanAcc-Werte
    """
    if path is None:
        path = screenshots_path
        
    results = []
    
    # Alle PNG-Dateien im Screenshots-Verzeichnis finden
    screenshot_files = [f for f in os.listdir(path) if f.endswith('.png')]
    
    # Nach Zeitstempel sortieren
    screenshot_files_with_timestamps = []
    for filename in screenshot_files:
        timestamp = extract_timestamp_from_filename(filename)
        if timestamp:
            screenshot_files_with_timestamps.append((timestamp, filename))
    
    # Nach Zeitstempel sortieren
    screenshot_files_with_timestamps.sort(key=lambda x: x[0])
    
    print(f"Verarbeite {len(screenshot_files_with_timestamps)} Screenshots...")
    
    for timestamp, filename in screenshot_files_with_timestamps:
        file_path = os.path.join(path, filename)
        
        try:
            # Bild laden
            image = Image.open(file_path)
            
            # Text extrahieren
            extracted_text = pytesseract.image_to_string(image, lang='deu+eng')
            
            # Werte extrahieren
            mean_acc = extract_meanAcc_from_text(extracted_text)
            siv = extract_siv_from_text(extracted_text)
            sip = extract_sip_from_text(extracted_text)
            pdop = extract_pdop_from_text(extracted_text)
            
            result = {
                'timestamp': timestamp,
                'filename': filename,
                'meanAcc': mean_acc,
                'siv': siv,
                'sip': sip,
                'pdop': pdop,
                'extracted_text': extracted_text
            }
            
            results.append(result)
            
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {filename} - meanAcc: {mean_acc}, siv: {siv}, sip: {sip}, pdop: {pdop}")
            
        except Exception as e:
            print(f"Fehler bei {filename}: {e}")
    
    return results

# Hauptprogramm
if __name__ == "__main__":
    # HIER PFAD EINSTELLEN:
    screenshots_path = r'C:\Users\J_Dei\OneDrive\Desktop\Screenshots\TH Test'  # Pfad zu deinen Screenshots hier eintragen
    
    # Screenshots verarbeiten
    results = process_screenshots(screenshots_path)
    
    # Ergebnisse in DataFrame speichern
    df_results = pd.DataFrame(results)
    
    # Nur Einträge mit allen gefundenen Werten (vollständige Datenpunkte)
    df_valid = df_results[
        (df_results['meanAcc'].notna()) & 
        (df_results['siv'].notna()) & 
        (df_results['sip'].notna()) & 
        (df_results['pdop'].notna())
    ]
    
    print(f"\n=== ZUSAMMENFASSUNG ===")
    print(f"Gesamt verarbeitete Screenshots: {len(results)}")
    print(f"Screenshots mit vollständigen Datensätzen: {len(df_valid)}")
    
    if len(df_valid) > 0:
        print(f"Durchschnittlicher meanAcc-Wert: {df_valid['meanAcc'].mean():.4f}")
        print(f"Minimum meanAcc: {df_valid['meanAcc'].min():.4f}")
        print(f"Maximum meanAcc: {df_valid['meanAcc'].max():.4f}")
        
        # CSV mit vollständigen Datenpunkten erstellen
        if len(df_valid) > 0:
            # Startzeit als Referenz
            start_time = df_valid['timestamp'].min()
            
            # Zeit in Stunden seit Start berechnen
            df_csv = pd.DataFrame({
                'time_hours': ((df_valid['timestamp'] - start_time).dt.total_seconds() / 3600).round(4),
                'meanAcc': df_valid['meanAcc'],
                'siv': df_valid['siv'],
                'sip': df_valid['sip'],
                'pdop': df_valid['pdop']
            })
            
            # Ergebnisse in CSV speichern
            df_csv.to_csv('meanAcc_auswertung_TH.csv', index=False)
            print(f"\nErgebnisse gespeichert in: meanAcc_auswertung.csv")
            print(f"CSV enthält {len(df_csv)} vollständige Datenpunkte")
    
    # Alle vollständigen Ergebnisse anzeigen (optional)
    print(f"\n=== ALLE VOLLSTÄNDIGEN DATENPUNKTE ===")
    for _, result in df_valid.iterrows():
        print(f"{result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: meanAcc={result['meanAcc']}, siv={result['siv']}, sip={result['sip']}, pdop={result['pdop']}")

