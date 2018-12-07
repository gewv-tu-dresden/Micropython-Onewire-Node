from time import sleep
from ds2480b import DS2480b, CRCError ,NoTempError
from machine import Pin
from cayennelpp import CayenneLPP
from button import Button
import machine
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
NO_TEMP_ERROR = -320
NO_TEMPRATUR_MEASURED = -310
UART_ERROR = -300
CRC_ERROR = -290
UNKNOWN_ERROR = -280

# config IO
# myled = Pin('P2', mode=Pin.OUT) Remove this, becouse inbuild led is on P2 too
case_button = Button('P8', longms=500)

def debug(message):
    "print message if debug == 1"
    if DEBUG:
        print(message)

def log(message):
    """message to terminal"""
    print(message)

# helper functions
def set_rgb_color(color):
    """change local led colour"""
    pycom.rgbled(color)
    global RGBCOLOR
    RGBCOLOR = color

#prüfen ob exclude.dat auf dem lopy4 vorhanden ist
if 'exclude.dat' in os.listdir():
    #laden der datei und in ein sep. Array speichern
    f = open('exclude.dat',"r")
    exclude = f.read()
    log('{} ausgeschlossene Sensoren'.format(exclude))
    exclude = exclude.split(';')
    f.close()
else:
    #erzeugen der datei
    f = open('exclude.dat', 'w')
    exclude = ("-1;")
    f.write(exclude)
    debug("init file 'exclude.dat'@"+exclude)
    exclude = exclude.split(";")
    f.close()

def printid(array):
    "print sensor id in hex"
    i = 0
    for i in range(0, len(array)):
        log(hex(array[i]))

def senditems():
    "send temps"
    log("Send temps to app server.")
    debug("Payloadsize: {}".format(lpp.get_size()))
    lpp.send(reset_payload=True)

# register callback for pins
def toggle_measuring():
    global MEASURE

    pycom.rgbled(TOGGLE_MEASURING_COLOR)
    MEASURE = not MEASURE

    if MEASURE:
        log('Measuring on')
        set_rgb_color(MEASURING_COLOR)
    else:
        log('Measuring off')
        set_rgb_color(NO_MEASURING_COLOR)

def toggle_debug():
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

case_button.short = toggle_measuring
case_button.long = toggle_debug

log('*******************Testprogramm DS2480B************************')
VAR = DS2480b(debug=DEBUG)
VAR.initrs232(1)

# Connect state with onewire interface
state.onewire_interface = VAR

log("search... please wait... ;-)")
VAR.getallid()
VAR.update_state(state)

clientno = VAR.checkdevices()
log("find {}x DS19B20 Sensor and {}x DS1920 Sensor".format(VAR.ds19b20no, VAR.ds1920no))

log("initialize cayennelpp")
lpp = CayenneLPP(size=51, sock=s)

go = True
riegel = True
turns = 0
i = 0
err_count = [0]*len(VAR.romstorage)
DEBUG = 1

while True:
    pycom.rgbled(RGBCOLOR)

    # only every 30 reads a package should send
    sendThisTurn = 0

    if MEASURE:
        i+=1

        if (VAR.ds19b20no == 0 and VAR.ds1920no == 0):
            #wdt.init(1000000)
            wdt.feed()
            #ggf. wdt.deinit() ?
            VAR.getallid()
            #wdt.init(60000)

        log("Abfrage " + str(i) + ": ")
        VAR.converttemp()

        for j in range(0, VAR.ds19b20no + VAR.ds1920no-1):
            if (str(j) in exclude):
                log("Fehlerhaften Sensor No.{} uebersprungen.".format(j+1))
                continue

            try:
                rom_storage = VAR.romstorage[j]
                acq_temp = VAR.acquiretemp(j)
                id = "".join(map(str, rom_storage))

                #Anpassung onewire Ring --> defekte Sensoren???
                if VAR.resetflag:
                    err_count[j] = err_count[j] + 1
                    log('Sensor No. {} --> Reset Err {}'.format(j+1,err_count[j]))
                    if err_count[j] == 5:
                        log("Err No.{} TempSensor: {}".format(j+1, rom_storage))
                        f = open("exclude.dat", "a+")
                        f.write(str(j)+";")
                        f.close()
                        machine.reset()
                else:
                    err_count[j] = 0
                    lpp.add_temperature(acq_temp, j)

                    # update the state
                    state.update_sensor(id, acq_temp)
                    debug("{} {} 'C'".format(rom_storage, acq_temp))

                    if not lpp.is_within_size_limit(2):
                        senditems()
                        debug("Next sensor overflow package size.")
                    else:
                        if acq_temp >= -55.0 and acq_temp <= 125.0:
                            lpp.add_temperature(acq_temp, j)

            # error codes added to an second channel
            except CRCError:
                if not lpp.is_within_size_limit(2):
                    senditems()
                    debug("Next exception overflow package size.")
                else:
                    lpp.add_temperature(CRC_ERROR, j)
            except NoTempError:
                if not lpp.is_within_size_limit(2):
                    senditems()
                    debug("Next exception overflow package size.")
                else:
                    lpp.add_temperature(NO_TEMPRATUR_MEASURED, j)

            except Exception as e:
                log('--- Unknown Exception ---')
                sys.print_exception(e)
                log('----------------------------')

                if not lpp.is_within_size_limit(2):
                    senditems()
                    debug("Next exception overflow package size.")
                else:
                    lpp.add_temperature(UNKNOWN_ERROR, j)


        # send the data after read all
        if lpp.get_size():
            senditems()

    pycom.rgbled(RGBOFF)
    wdt.feed()
    debug('Feed the watchdog.')
    sleep(10)

VAR.closers232()
