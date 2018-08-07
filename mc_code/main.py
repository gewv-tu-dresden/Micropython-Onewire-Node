from time import sleep
from ds2480b import *
from machine import Pin
from cayennelpp import CayenneLPP
import pycom

VAR = None
MEASURE = True
DEBUG = False
MEASURING_COLOR = 0x007f00
NO_MEASURING_COLOR = 0x7f0000
TOGGLE_MEASURING_COLOR = 0x7f7f00
TOGGLE_DEBUG_COLOR = 0x007f7f
RGBCOLOR = 0x007f00

# config IO
# myled = Pin('P2', mode=Pin.OUT) Remove this, becouse inbuild led is on P2 too
lock_pin = Pin('P8', mode=Pin.IN, pull=Pin.PULL_UP)
debug_pin = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)

# helper functions
def set_rgb_color(color):
    pycom.rgbled(color)
    global RGBCOLOR
    RGBCOLOR = color

def printid(array):
    "print sensor id in hex"
    i = 0
    for i in range(0, len(array)):
        print(hex(array[i]))

def debug(message):
    if DEBUG:
        print(message)

def log(message):
    print(message)

# register callback for pins
def toggle_measuring(arg):
    global MEASURE
    pycom.rgbled(TOGGLE_MEASURING_COLOR)
    MEASURE = not MEASURE
    if MEASURE:
        log('Measuring on')
        set_rgb_color(MEASURING_COLOR)
    else:
        log('Measuring off')
        set_rgb_color(NO_MEASURING_COLOR)

lock_pin.callback(Pin.IRQ_RISING, toggle_measuring)

def toggle_debug(arg):
    global DEBUG
    global VAR

    pycom.rgbled(TOGGLE_DEBUG_COLOR)
    DEBUG = not DEBUG
    if VAR is not None:
        VAR.debug = DEBUG

    sleep(0.5)
    set_rgb_color(RGBCOLOR)

debug_pin.callback(Pin.IRQ_RISING, toggle_debug)

log('*******************Testprogramm DS2480B************************')
VAR = DS2480b(debug=DEBUG)
VAR.set232parameter(port=1)
VAR.initrs232()

log("search...")
VAR.getallid()
clientno = VAR.checkdevices()
# VAR.debug = 0

log("initialize cayennelpp")
lpp = CayenneLPP(size=64, sock=s)

go = True
riegel = True
turns = 0
i = 0

while True:
    pycom.rgbled(RGBCOLOR)

    if MEASURE:

        i+=1
        VAR.converttemp()
        print("Abfrage " + str(i) + ": ")
        sleep(1.8)
        for j in range(0, clientno-1):
            rom_storage = VAR.romstorage[j]
            acq_temp = VAR.acquiretemp(j)

            if not lpp.is_within_size_limit(2):
                print("Next sensor overflow package size.")
            else:
                lpp.add_temperature(acq_temp, j)

            print("{} {} 'C'".format(rom_storage, acq_temp))

        print("Send temps to app server.")
        print("Payloadsize: {}".format(lpp.get_size()))
        lpp.send(reset_payload=True)

    sleep(10)

VAR.closers232()
