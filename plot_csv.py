import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def plot_meanAcc_data(csv_file='meanAcc_auswertung.csv'):
    """
    Plottet die meanAcc-Daten aus der CSV-Datei mit drei Subplots
    """
    # Prüfen ob CSV-Datei existiert
    if not os.path.exists(csv_file):
        print(f"Fehler: CSV-Datei '{csv_file}' nicht gefunden!")
        return
    
    # CSV-Datei laden
    try:
        df = pd.read_csv(csv_file)
        print(f"CSV-Datei geladen: {len(df)} Datenpunkte")
    except Exception as e:
        print(f"Fehler beim Laden der CSV-Datei: {e}")
        return
    
    # Prüfen ob die erwarteten Spalten vorhanden sind
    required_columns = ['time_hours', 'meanAcc', 'siv', 'sip', 'pdop']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Fehler: CSV-Datei muss folgende Spalten enthalten: {missing_columns}")
        return
    
    # Figure mit drei Subplots erstellen
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: meanAcc
    ax1.plot(df['time_hours'], df['meanAcc'], 'b-', linewidth=1.5, marker='o', markersize=3)
    ax1.set_ylabel('meanAcc')
    ax1.set_title('SVIN Daten über Zeit')
    ax1.grid(True, alpha=0.3)
    
    # Mittelwert für meanAcc
    mean_acc = df['meanAcc'].mean()
    ax1.axhline(y=mean_acc, color='r', linestyle='--', alpha=0.7, label=f'Mittelwert: {mean_acc:.4f}')
    ax1.legend()
    
    # Plot 2: siv und sip
    ax2.plot(df['time_hours'], df['siv'], 'g-', linewidth=1.5, marker='s', markersize=3, label='siv')
    ax2.plot(df['time_hours'], df['sip'], 'orange', linewidth=1.5, marker='^', markersize=3, label='sip')
    ax2.set_ylabel('Satelliten Anzahl')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: pdop
    ax3.plot(df['time_hours'], df['pdop'], 'm-', linewidth=1.5, marker='d', markersize=3)
    ax3.set_ylabel('PDOP')
    ax3.set_xlabel('Zeit (Stunden)')
    ax3.grid(True, alpha=0.3)
    
    # Mittelwert für pdop
    mean_pdop = df['pdop'].mean()
    ax3.axhline(y=mean_pdop, color='r', linestyle='--', alpha=0.7, label=f'Mittelwert: {mean_pdop:.2f}')
    ax3.legend()
    
    # Layout anpassen
    plt.tight_layout()
    
    # Plot als Datei speichern
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    plot_filename = f"plot_{base_name}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot gespeichert als: {plot_filename}")
    
    # Plot anzeigen
    plt.show()
    
    # Statistiken ausgeben
    print(f"\n=== STATISTIKEN ===")
    print(f"Anzahl Datenpunkte: {len(df)}")
    print(f"Zeitraum: {df['time_hours'].min():.2f} - {df['time_hours'].max():.2f} Stunden")
    print(f"\nmeanAcc:")
    print(f"  Mittelwert: {df['meanAcc'].mean():.4f}")
    print(f"  Minimum: {df['meanAcc'].min():.4f}")
    print(f"  Maximum: {df['meanAcc'].max():.4f}")
    print(f"  Standardabweichung: {df['meanAcc'].std():.4f}")
    print(f"\nsiv:")
    print(f"  Mittelwert: {df['siv'].mean():.1f}")
    print(f"  Minimum: {df['siv'].min()}")
    print(f"  Maximum: {df['siv'].max()}")
    print(f"\nsip:")
    print(f"  Mittelwert: {df['sip'].mean():.1f}")
    print(f"  Minimum: {df['sip'].min()}")
    print(f"  Maximum: {df['sip'].max()}")
    print(f"\npdop:")
    print(f"  Mittelwert: {df['pdop'].mean():.2f}")
    print(f"  Minimum: {df['pdop'].min():.2f}")
    print(f"  Maximum: {df['pdop'].max():.2f}")
    print(f"  Standardabweichung: {df['pdop'].std():.2f}")

def find_meanAcc_csv_files(directory='.'):
    """
    Findet alle CSV-Dateien im Verzeichnis, die 'meanAcc' im Namen haben
    """
    pattern = os.path.join(directory, '*meanAcc*.csv')
    csv_files = glob.glob(pattern)
    return sorted(csv_files)

def plot_all_meanAcc_files(directory='.'):
    """
    Plottet alle CSV-Dateien mit 'meanAcc' im Namen nacheinander
    """
    csv_files = find_meanAcc_csv_files(directory)
    
    if not csv_files:
        print(f"Keine CSV-Dateien mit 'meanAcc' im Namen im Verzeichnis '{directory}' gefunden!")
        return
    
    print(f"Gefundene CSV-Dateien: {len(csv_files)}")
    for file in csv_files:
        print(f"  - {os.path.basename(file)}")
    
    print(f"\nPlots werden im Verzeichnis '{directory}' gespeichert.")
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\n{'='*50}")
        print(f"Plotte Datei {i}/{len(csv_files)}: {os.path.basename(csv_file)}")
        print(f"{'='*50}")
        
        plot_meanAcc_data(csv_file)
        
        # Nach jedem Plot warten bis Benutzer weiter macht (außer beim letzten)
        if i < len(csv_files):
            input("\nDrücke Enter für den nächsten Plot...")
    
    print(f"\n{'='*50}")
    print(f"Alle {len(csv_files)} Plots erfolgreich erstellt und gespeichert!")
    print(f"{'='*50}")

if __name__ == "__main__":
    # HIER VERZEICHNIS EINSTELLEN (optional):
    directory = '.'  # Aktuelles Verzeichnis oder gewünschten Pfad hier eintragen
    
    plot_all_meanAcc_files(directory)
