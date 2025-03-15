import os
import csv
from datetime import datetime

DATA_CSV = "mornfeels_data.csv"
SETTINGS_FILE = "settings.csv"

def init_csv(file_path):
    """Erstellt die CSV-Datei mit Headern, falls sie nicht existiert."""
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Date', 'Time', 'Value', 'Note'])

def save_entry(file_path, mood, note):
    """Speichert einen neuen Eintrag in der CSV-Datei mit aktuellem Datum und Uhrzeit."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([date_str, time_str, mood, note])

def load_unique_dates_from_csv():
    """
    Liest DATA_CSV und gibt eine sortierte Liste der eindeutigen Daten (YYYY-MM-DD) zurück.
    """
    if not os.path.exists(DATA_CSV):
        print("DEBUG: DATA_CSV not found.")
        return []
    dates = set()
    with open(DATA_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader, None)  # Header überspringen
        for row in reader:
            if len(row) >= 3:
                dates.add(row[0])
    unique_dates = sorted(dates)
    print("DEBUG: Unique dates loaded:", unique_dates)
    return unique_dates

def filter_data_by_dates(start_date, end_date):
    """
    Filtert die Daten aus DATA_CSV zwischen start_date und end_date (inklusive).
    Erwartet Datumsangaben im Format YYYY-MM-DD.
    Gibt eine Liste der Zeilen zurück.
    """
    data = []
    with open(DATA_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader, None)  # Header überspringen
        for row in reader:
            if len(row) >= 3:
                d = row[0]
                if start_date <= d <= end_date:
                    data.append(row)
    print(f"DEBUG: Filtered data count between {start_date} and {end_date}: {len(data)}")
    return data

def load_settings():
    """Lädt Erinnerungstermine aus SETTINGS_FILE als Liste von (Stunde, Minute)-Tupeln."""
    if not os.path.exists(SETTINGS_FILE):
        return [(8, 0), (12, 0), (16, 0), (20, 0)]
    times = []
    with open(SETTINGS_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if len(row) == 2:
                try:
                    hour = int(row[0])
                    minute = int(row[1])
                    times.append((hour, minute))
                except ValueError:
                    pass
    return sorted(times)

def save_settings(times):
    """Speichert die Liste der (Stunde, Minute)-Tupel in SETTINGS_FILE."""
    with open(SETTINGS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for (hour, minute) in times:
            writer.writerow([hour, minute])

