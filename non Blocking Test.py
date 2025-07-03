import machine
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
        
        

while True:
    if not isIdentified:
        Identify()
        continue
    c = read_message()
    if c != None:
        handle_command(c)
    print("UNITY: KEYBOARD: A")
    time.sleep(2)





