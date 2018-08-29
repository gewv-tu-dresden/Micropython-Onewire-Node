from time import sleep
from ds2480b import DS2480b, CRCError, NoTempError
from machine import Pin
from cayennelpp import CayenneLPP
import sys
import pycom

VAR = None
MEASURE = True
DEBUG = False
MEASURING_COLOR = 0x007f00
NO_MEASURING_COLOR = 0x7f0000
TOGGLE_MEASURING_COLOR = 0x7f7f00
TOGGLE_DEBUG_COLOR = 0x007f7f
RGBCOLOR = 0x007f00
RGBOFF = 0x050505

# error codes
NO_TEMPRATUR_MEASURED = 0
UART_ERROR = 1
CRC_ERROR = 2
UNKNOWN_ERROR = 3

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

    if DEBUG:
        wser.start()
    else:
        wser.stop()

    sleep(0.5)
    pycom.rgbled(RGBCOLOR)

debug_pin.callback(Pin.IRQ_RISING, toggle_debug)

wser.start()
log('*******************Testprogramm DS2480B************************')
VAR = DS2480b(debug=DEBUG, temperature=-300)
VAR.set232parameter(port=1)
VAR.initrs232()

log("search...")
VAR.getallid()
clientno = VAR.checkdevices()
# VAR.debug = 0
for rom in VAR.romstorage:
    if rom is not None:
        name = " ".join(map(hex, rom))
        id = "".join(map(str, rom))
        state.add_sensor(id, name)

log("initialize cayennelpp")
lpp = CayenneLPP(size=51, sock=s)

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
            try:
                rom_storage = VAR.romstorage[j]
                acq_temp = VAR.acquiretemp(j)
                id = "".join(map(str, rom_storage))

                if not lpp.is_within_size_limit(2):
                    print("Next sensor overflow package size.")
                else:
                    if acq_temp >= -55.0 and acq_temp <= 125.0:
                        lpp.add_temperature(acq_temp, j)

                state.update_sensor(id, acq_temp)
                debug("{} {} 'C'".format(rom_storage, acq_temp))

            # error codes added to an second channel
            except CRCError:
                if not lpp.is_within_size_limit(2):
                    print("Next exception overflow package size.")
                    lpp.add_digital_input(CRC_ERROR, j+clientno)
            except NoTempError:
                if not lpp.is_within_size_limit(2):
                    print("Next exception overflow package size.")
                    lpp.add_digital_input(NO_TEMPRATUR_MEASURED, j+clientno)

            except Exception as e:
                log('--- Unknown Exception ---')
                sys.print_exception(e)
                log('----------------------------')

                if not lpp.is_within_size_limit(2):
                    print("Next exception overflow package size.")
                    lpp.add_digital_input(UNKNOWN_ERROR, j+clientno)


        print("Send temps to app server.")
        print("Payloadsize: {}".format(lpp.get_size()))
        lpp.send(reset_payload=True)

    pycom.rgbled(RGBOFF)
    # wdt.feed()
    debug('Feed the watchdog.')
    sleep(10)

VAR.closers232()
