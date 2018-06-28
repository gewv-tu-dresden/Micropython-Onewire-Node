# boot.py -- run on boot-up
import machine
import os
import time
import ubinascii as binascii
import pycom
from machine import WDT

###  Initialize ###

# Initialize Uart
uart = machine.UART(0, 115200) # disable these two lines if you don't want serial access
os.dupterm(uart)

# LoRa in LORAWAN mode.
#lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# Initialize watchdog
#wdt = WDT(timeout=60000)

####################

pycom.heartbeat(False)
pycom.rgbled(0x220000) # red

### Configure Lora ###
if machine.reset_cause() == machine.WDT_RESET:
    debug_log("Watchdog rescued us.")

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    debug_log("Woke up from deepsleep.")
    lora.nvram_restore()

if machine.reset_cause() == machine.DEEPSLEEP_RESET and lora.has_joined():
    debug_log("Skipping joining.")
else:
    pass
    #debug_log("Try to join TTN")
    # create an OTAA authentication parameters
    #dev_eui = binascii.unhexlify('005CEF018F9012A7')
    #app_eui = binascii.unhexlify('70B3D57ED0006FD4')
    #app_key = binascii.unhexlify('CBD1B7A0C667F2CE64B16098BD1A5AFE')

    # join a network using OTAA (Over the Air Activation)
    #lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    #while not lora.has_joined():
    #    time.sleep(2.5)
    #    debug_log('Not yet joined...')

    #debug_log('Joined.')

# create a LoRa socket
#s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
#s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
######################
