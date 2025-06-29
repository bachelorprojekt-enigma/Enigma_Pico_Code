import time
from machine import Pin
import sys


# Reihen + GPIO 2-4
reihen = [Pin(i, Pin.OUT) for i in range(2, 5)]
# Reihen + GPIO 5-13
spalten = [Pin(i, Pin.OUT) for i in range(5, 14)]

# Tastenfeld-Zuordnung: [Reihe][Spalte]
tastenfeld = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],    # Reihe 0
    ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'],    # Reihe 1
    ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', None]    # Reihe 2
]

def leds_aus():
    for z in reihen:
        z.value(0)
    for s in spalten:
        s.value(1)

def led_einschalten(reihe, spalten):
    leds_aus()
    if reihe < len(reihen) and spalte < len(spalten):
        reihen[reihe].value(1)
        spalten[spalte].value(0)

def buchstabe_finden(buchstabe):
    for reihe in range(len(tastenfeld)):
        for spalte in range(len(tastenfeld[reihe])):
            if tastenfeld[reihe][spalte].lower() == buchstabe.lower():
                return reihe, spalte
    return None, None


while True:
    eingabe = sys.stdin.readline().strip().lower()
    woerter = eingabe.split()

    if len(woerter) >= 2 and woerter[0] == "LED:":
        buchstabe = woerter[1]
        reihe, spalte = buchstabe_finden(buchstabe)
        
        if reihe is not None and spalte is not None:
            led_einschalten(reihe, spalte)
        else:
            pass
            #Hier könnte man ein Fehlercode einbauen falls nötig
    else:
        pass
        #Hier könnte man ein Fehlercode einbauen falls nötig
    time.sleep(1)
