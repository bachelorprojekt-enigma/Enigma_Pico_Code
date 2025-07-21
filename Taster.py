from machine import Pin
import time
import sys
import uselect

identifier = "KEYBOARD_CONTROLLER"
isIdentified = False

#spoll erlaubt es zu gucken ob es nachrichten gibt ohne den Pico zu Blockieren
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def read_message():
    if spoll.poll(0):	#Nur wenn eine Nachricht da ist, die Nachricht lesen
        return sys.stdin.readline()
    return None
    
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
    "RESET": reset
}


def handle_command(cmd):
    action = commands.get(cmd.strip().upper())
    if action:
        action()
    else:
        print("Unknown Command:", cmd)
        
def test_handler(cmd):
    return

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
        


# Reihen + GPIO 2-4
reihen = [Pin(i, Pin.OUT) for i in range(2, 5)]

# Spalten + GPIO 5-13
spalten = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(6, 15)]

# Tastenzuordnung: [Reihe][Spalte]
tastenfeld = [
    ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O'],    # Reihe 0
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', None],   # Reihe 1
    ['P', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', 'L']     # Reihe 2 (letztes Feld leer)
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
    if not isIdentified:
        Identify()
        continue
    c = read_message()
    if c != None:
        handle_command(c)uselect
    
    tasten_scannen()
    time.sleep(3)
