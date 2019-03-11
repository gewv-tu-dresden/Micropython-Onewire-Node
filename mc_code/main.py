from time import sleep
from ds2480b import DS2480b, CRCError, NoTempError
from state import RF_MODES
import machine
import sys
import pycom
from utils import print_ids, debug, log

VAR = None
MEASURE = True
DEBUG = False

# error codes
NO_TEMP_ERROR = -320
NO_TEMPRATUR_MEASURED = -310
UART_ERROR = -300
CRC_ERROR = -290
UNKNOWN_ERROR = -280


# check if exclude.dat is on lopy
if 'exclude.dat' in os.listdir():
    # load the file in a seperate Array
    f = open('exclude.dat', "r")
    exclude = f.read()
    log('{} ausgeschlossene Sensoren'.format(exclude))
    exclude = exclude.split(';')
    f.close()
else:
    # make the file
    f = open('exclude.dat', 'w')
    exclude = ("-1;")
    f.write(exclude)
    debug("init file 'exclude.dat'@" + exclude, state.debug_mode)
    exclude = exclude.split(";")
    f.close()

log('*******************Testprogramm DS2480B************************')
VAR = DS2480b(debug=DEBUG)
VAR.initrs232(1)

# Connect state with onewire interface
state.onewire_interface = VAR

log("search... please wait... ;-)")
VAR.getallid()
debug("got all ids", state.debug_mode)
VAR.update_state(state)
debug("update state", state.debug_mode)

clientno = VAR.checkdevices()
log("find {}x DS19B20 Sensor and {}x DS1920 Sensor".format(
    VAR.ds19b20no, VAR.ds1920no))

i = 0
err_count = [0] * len(VAR.romstorage)

while True:
    debug("start new turn", state.debug_mode)
    pycom.rgbled(state.rgb_color)

    if MEASURE:
        i += 1

        if (VAR.ds19b20no == 0 and VAR.ds1920no == 0):
            wdt.feed()
            VAR.getallid()

        log("Abfrage " + str(i) + ": ")
        VAR.converttemp()

        for j in range(0, VAR.ds19b20no + VAR.ds1920no):
            if (str(j) in exclude):
                log("Fehlerhaften Sensor No.{} uebersprungen.".format(j + 1))
                continue

            try:
                rom_storage = VAR.romstorage[j]
                acq_temp = VAR.acquiretemp(j)
                id = "".join(map(str, rom_storage))

                #Anpassung onewire Ring --> defekte Sensoren???
                if VAR.resetflag:
                    err_count[j] = err_count[j] + 1
                    log('Sensor No. {} --> Reset Err {}'.format(
                        j + 1, err_count[j]))
                    if err_count[j] == 5:
                        log("Err No.{} TempSensor: {}".format(
                            j + 1, rom_storage))
                        f = open("exclude.dat", "a+")
                        f.write(str(j) + ";")
                        f.close()
                        machine.reset()
                else:
                    err_count[j] = 0
                    sender.add_temperature(acq_temp, j)

                    # update the state
                    state.update_sensor(id, acq_temp)
                    debug("{} {} 'C'".format(rom_storage, acq_temp), state.debug_mode)

                    if not sender.is_within_size_limit(2):
                        sender.send_items()
                        debug("Next sensor overflow package size.", state.debug_mode)
                    else:
                        if acq_temp >= -55.0 and acq_temp <= 125.0:
                            sender.add_temperature(acq_temp, j)

            # error codes added to an second channel
            except CRCError:
                if not sender.is_within_size_limit(2):
                    sender.send_items()
                    debug("Next exception overflow package size.", state.debug_mode)
                else:
                    sender.add_temperature(CRC_ERROR, j)
            except NoTempError:
                if not sender.is_within_size_limit(2):
                    sender.send_items()
                    debug("Next exception overflow package size.", state.debug_mode)
                else:
                    sender.add_temperature(NO_TEMPRATUR_MEASURED, j)

            except Exception as e:
                log('--- Unknown Exception ---')
                sys.print_exception(e)
                log('----------------------------')

                if not sender.is_within_size_limit(2):
                    sender.send_items()
                    debug("Next exception overflow package size.", state.debug_mode)
                else:
                    sender.add_temperature(UNKNOWN_ERROR, j)

        # send the data after read all
        if sender.get_size():
            sender.send_items()

    state.set_rgb_off()
    wdt.feed()
    debug('Feed the watchdog.', state.debug_mode)
    # send ever 5 min
    sleep(10)

VAR.closers232()
