# ==============================================================================
# Projekt: Enigma Steckbrett Emulator
# Autor: Sarah-Lena Janaschke & Alexander Jost
# Version: 4.1
# Beschreibung:
# Dieser Code implementiert einen Enigma-Steckbrett-Emulator auf einem Raspberry Pi Pico.
# Er erkennt physische Verbindungen zwischen 26 Klinkenanschlüssen (A-Z) und speichert diese
# als Buchstabenvertauschungen. Tastatureingaben über die serielle Schnittstelle werden
# durch die aktuelle Steckbrettkonfiguration verarbeitet. Eine integrierte Entprellung
# sorgt dafür, dass nur stabile Verbindungen erkannt werden.
# ==============================================================================

from machine import Pin      # Importiert die Pin-Klasse zur GPIO-Steuerung.
import time                  # Importiert das time-Modul für Zeitfunktionen.
import sys                   # Importiert das sys-Modul für Standard-I/O-Zugriff.
import select                # Importiert das select-Modul für nicht-blockierende Eingabeüberwachung.

# --- GPIO-Pin-Konfiguration für 26 Klinkenanschlüsse (A-Z) ---
# Liste der GPIO-Pin-Nummern auf dem Raspberry Pi Pico, die für die Klinkenanschlüsse verwendet werden.
# Die Reihenfolge entspricht den Buchstaben A bis Z. GP16 ist ausgelassen.
gpio_pins_fuer_steckbrett = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    17, 18, 19, 20, 21, 22, 26, 27, 28, 25
]

# Überprüft, ob die korrekte Anzahl von Pins für das Alphabet A-Z definiert ist.
if len(gpio_pins_fuer_steckbrett) != 26:
    raise ValueError(f"Fehler: {len(gpio_pins_fuer_steckbrett)} Pins angegeben, 26 für A-Z erwartet.")

# Dictionary, das jeden Buchstaben (A-Z) einem konfigurierten Pin-Objekt zuweist.
steckbrett_pin_objekte = {}
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

for i in range(len(alphabet)):
    buchstabe = alphabet[i]
    gpio_nummer = gpio_pins_fuer_steckbrett[i]
    # Konfiguriert den Pin als Eingang mit internem Pull-Up-Widerstand.
    # Pin ist HIGH (logisch 1) im offenen Zustand, LOW (logisch 0) bei Verbindung mit GND.
    steckbrett_pin_objekte[buchstabe] = Pin(gpio_nummer, Pin.IN, Pin.PULL_UP)

# --- Globale Variablen ---
# Speichert die aktuell bestätigten Buchstabenvertauschungen des Steckbretts.
# Format: {'A': 'B', 'B': 'A'}
aktuelle_zuordnung = {}

# Speichert temporär potenzielle Verbindungen und deren Erkennungszeitpunkt für die Entprellung.
# Format: {('Buchstabe1', 'Buchstabe2'): Zeitstempel_ms}
laufende_verbindungen = {}

# Die Zeit (in Millisekunden), die eine Verbindung stabil bestehen muss, um als gültig erkannt zu werden.
VERBINDUNG_HALTEZEIT_MS = 2000 # 2 Sekunden

# --- Funktionen ---

def aktualisiere_steckbrett_status():
    """
    Erkennt physische Verbindungen zwischen Klinkenanschlüssen und aktualisiert die Zuordnung.
    Implementiert eine Timer-basierte Entprellung für stabile Verbindungserkennung.
    """
    global aktuelle_zuordnung, laufende_verbindungen
    
    # Temporäres Dictionary für im aktuellen Scan bestätigte stabile Verbindungen.
    stabile_verbindungen_aktuell = {} 
    
    buchstaben = list(steckbrett_pin_objekte.keys())
    
    # Iteriert über alle möglichen Paare von Buchstaben, um Verbindungen zu prüfen.
    for i in range(len(buchstaben)):
        for j in range(i + 1, len(buchstaben)):
            buchstabe1 = buchstaben[i]
            buchstabe2 = buchstaben[j]
            
            # Erstellt einen eindeutigen Schlüssel für das Paar, unabhängig von der Reihenfolge.
            paar_schluessel = tuple(sorted((buchstabe1, buchstabe2))) 
            
            pin1 = steckbrett_pin_objekte[buchstabe1]
            pin2 = steckbrett_pin_objekte[buchstabe2]
            
            # Setzt Pin1 kurz als Ausgang auf LOW, um eine Verbindung zu testen.
            pin1.init(Pin.OUT, value=0) 
            time.sleep_us(100) # Kurze Verzögerung zur Stabilisierung.
            
            # Prüft den Zustand von Pin2. Wenn LOW, besteht eine Verbindung.
            ist_verbunden = (pin2.value() == 0) 
            
            # Setzt Pin1 sofort als Eingang mit Pull-Up zurück.
            pin1.init(Pin.IN, Pin.PULL_UP) 
            time.sleep_us(100) # Kurze Verzögerung zur Stabilisierung.

            aktuelle_zeit_ms = time.ticks_ms() # Aktueller Zeitstempel in Millisekunden.

            if ist_verbunden:
                # Wenn eine Verbindung erkannt wird:
                if paar_schluessel not in laufende_verbindungen:
                    # Speichert den Startzeitpunkt der neu erkannten Verbindung.
                    laufende_verbindungen[paar_schluessel] = aktuelle_zeit_ms
                else:
                    # Prüft, ob die Verbindung die erforderliche Haltezeit überschritten hat.
                    if time.ticks_diff(aktuelle_zeit_ms, laufende_verbindungen[paar_schluessel]) >= VERBINDUNG_HALTEZEIT_MS:
                        # Verbindung ist stabil, fügt sie zu den bestätigten Verbindungen hinzu.
                        stabile_verbindungen_aktuell[buchstabe1] = buchstabe2
                        stabile_verbindungen_aktuell[buchstabe2] = buchstabe1
            else:
                # Wenn die Verbindung nicht (mehr) besteht:
                # Entfernt sie aus den laufenden Verbindungen, falls vorhanden (setzt den Timer zurück).
                if paar_schluessel in laufende_verbindungen:
                    del laufende_verbindungen[paar_schluessel]

    # Aktualisiert die globale Zuordnung mit den im aktuellen Scan bestätigten Verbindungen.
    neue_zuordnung = {}
    for buchstabe_a, buchstabe_b in stabile_verbindungen_aktuell.items():
        neue_zuordnung[buchstabe_a] = buchstabe_b

    # Gibt eine Statusmeldung aus, wenn sich die Steckbrett-Zuordnung geändert hat.
    if aktuelle_zuordnung != neue_zuordnung:
        aktuelle_zuordnung = neue_zuordnung
        print("\n--- Steckbrett-Zuordnung aktualisiert ---")
        if not aktuelle_zuordnung:
            print("  Keine Vertauschungen aktiv.")
        else:
            # Zeigt jedes Paar nur einmal an (z.B. "A ist B", nicht auch "B ist A").
            angezeigte_paare = set() 
            for k, v in aktuelle_zuordnung.items():
                paar = tuple(sorted((k, v)))
                if paar not in angezeigte_paare:
                    print(f"  {k} ist jetzt {v}")
                    angezeigte_paare.add(paar)

def verarbeite_buchstaben(eingabe_buchstabe):
    """
    Verarbeitet einen Eingabebuchstaben gemäß der aktuellen Steckbrett-Zuordnung.
    """
    # Gibt den vertauschten Buchstaben zurück, falls eine Zuordnung existiert,
    # ansonsten den Originalbuchstaben.
    return aktuelle_zuordnung.get(eingabe_buchstabe, eingabe_buchstabe) 

# --- Hauptprogramm-Schleife ---

# Startmeldungen für den Benutzer.
print("--- Enigma-Steckbrett-Emulator gestartet (26 Buchstaben A-Z) ---")
print(f"Verbindungen müssen {VERBINDUNG_HALTEZEIT_MS / 1000} Sekunden stabil sein.")
print("Geben Sie Buchstaben (A-Z) über die Tastatur ein und drücken Sie ENTER.")
print("Hinweis: Verbinden Sie Klinkenanschlüsse für Vertauschungen.")

# Initialisiert das Polling-Objekt für die nicht-blockierende serielle Eingabe.
eingabe_poller = select.poll()
eingabe_poller.register(sys.stdin, select.POLLIN)

while True: # Endlosschleife des Programms.
    aktualisiere_steckbrett_status() # Überprüft den Steckbrett-Status.
    
    # Prüft auf verfügbare Tastatureingaben.
    if eingabe_poller.poll(0):
        zeichen_code = sys.stdin.read(1) # Liest ein einzelnes Zeichen.
        if zeichen_code:
            eingabe_buchstabe = zeichen_code.upper() # Konvertiert zu Großbuchstaben.

            # Verarbeitet nur Buchstaben von A bis Z.
            if 'A' <= eingabe_buchstabe <= 'Z':
                if eingabe_buchstabe in steckbrett_pin_objekte:
                    ausgabe_buchstabe = verarbeite_buchstaben(eingabe_buchstabe)
                    print(f"Eingabe: {eingabe_buchstabe}, Ausgabe: {ausgabe_buchstabe}")
                else:
                    print(f"WARNUNG: Buchstabe '{eingabe_buchstabe}' hat keinen zugewiesenen Anschluss.")
            elif eingabe_buchstabe == '\n' or eingabe_buchstabe == '\r':
                # Ignoriert Zeilenumbrüche.
                pass
            else:
                print(f"Ungültige Eingabe: '{eingabe_buchstabe}'. Bitte nur Buchstaben A-Z eingeben.")

    time.sleep_ms(10) # Kurze Pause zur CPU-Entlastung.