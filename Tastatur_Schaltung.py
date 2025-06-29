import time
from machine import Pin
import sys


# Reihen + GPIO 2-4
reihen = [Pin(i, Pin.OUT) for i in range(2, 5)]

# Spalten + GPIO 5-13
spalten = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(5, 14)]

# Tastenzuordnung: [Reihe][Spalte]
tastenfeld = [
    ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],    # Reihe 0
    ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'],    # Reihe 1
    ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', None]    # Reihe 2 (letztes Feld leer)
]

def tasten_scannen():
    for reihen_index in range(len(reihen)):
        for r in range(len(reihen)):
            reihen[r].value(1)

        reihen[reihen_index].value(0)

        for spalten_index in range(len(spalten)):
            if not spalten[spalten_index].value():
                taste = tastenfeld[reihen_index][spalten_index]
                if taste is not None:
                    print("LED: ", taste)
                    time.sleep(0.3)

while True:
    tasten_scannen()
    time.sleep(0.3) 