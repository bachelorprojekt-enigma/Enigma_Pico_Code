import time
from machine import Pin
import sys
import uselect

identifier = "LED_CONTROLLER"
isIdentified = False

#spoll erlaubt es zu gucken ob es nachrichten gibt ohne den Pico zu Blockieren
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def read_message():
    if spoll.poll(0):	#Nur wenn eine Nachricht da ist, die Nachricht lesen
        return sys.stdin.readline()
    return None

def led_on():
    print("LED_CONTROLLER: LED1: ON")
    
def led_off():
    print("turning led 1 off")
    
def sendIdent():
    print(identifier)

def sendReply():
    print(identifier + " Replies")

def reset():
    global isIdentified
    isIdentified = False
    
    
commands = {
    "SEND_IDENT": sendIdent,
    "SEND_REPLY": sendReply,
    "LED1: ON": led_on,
    "LED1: OFF": led_off,
    "RESET": reset
}

# Reihen + GPIO 2-4
reihen = [Pin(i, Pin.OUT) for i in range(0, 3)]
# Reihen + GPIO 5-13
spalten = [Pin(i, Pin.OUT) for i in range(17, 29)]

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

def led_einschalten(reihe, spalte):
    print("doing smth")
    leds_aus()
    if reihe < len(reihen) and spalte < len(spalten):
        reihen[reihe].value(1)
        spalten[spalte].value(0)
        time.sleep(2)
        leds_aus()

def buchstabe_finden(buchstabe):
    for reihe in range(len(tastenfeld)):
        for spalte in range(len(tastenfeld[reihe])):
            if tastenfeld[reihe][spalte] == buchstabe:
                print("buchstabe gefunden")
                return reihe, spalte
    return None, None

def Identify():
    global isIdentified
    line = read_message()
    if line != None:
        line = line.strip()
        if line == "SEND_IDENT":
            print(identifier)
            isIdentified = True
    else:
        return


while True:
    if not isIdentified:
        Identify()
        continue

        
    eingabe = read_message()
    if eingabe != None:
        print(eingabe)
        woerter = eingabe.split(":")
        woerter = [word.strip() for word in woerter]
        #for word in woerter:
         #   word.strip()
          #  print(word)
    
        if len(woerter) <= 2: #and woerter[0] == "LED":
            buchstabe = woerter[1]
            print(buchstabe)
            reihe, spalte = buchstabe_finden(buchstabe)
            
            if reihe is not None and spalte is not None:
                led_einschalten(reihe, spalte)
            else:
                pass
                #Hier könnte man ein Fehlercode einbauen falls nötig
        else:
            pass
            #Hier könnte man ein Fehlercode einbauen falls nötig


