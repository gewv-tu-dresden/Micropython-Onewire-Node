import machine
import os
import time
import ubinascii as binascii
import pycom
from machine import WDT
from network import LoRa
import socket
from webserver import Webserver

### Const ###
RED = 0x220000
YELLOW = 0x222200
DEV_EUI = '004BA9B9A7199F28'
APP_EUI = '70B3D57ED00109EF'
APP_KEY = 'B0B863F19717BB0BB5D73370BA08A252'

###  Initialize ###

# Initialize Uart
uart = machine.UART(0, 115200) # disable these two lines if you don't want serial access
os.dupterm(uart)

# LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# Initialize watchdog
# wdt = WDT(timeout=60000)

wser = Webserver(dev_eui=DEV_EUI)
wser.start()

time.sleep(10)

wser.stop()

time.sleep(10)

wser.start()

####################

pycom.heartbeat(False)
pycom.rgbled(RED) # red

### Configure Lora ###
if machine.reset_cause() == machine.WDT_RESET:
    print("Watchdog rescued us.")

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Woke up from deepsleep.")
    lora.nvram_restore()

if machine.reset_cause() == machine.DEEPSLEEP_RESET and lora.has_joined():
    print("Skipping joining.")
else:
    print("Try to join TTN")
    # create an OTAA authentication parameters
    dev_eui = binascii.unhexlify(DEV_EUI)
    app_eui = binascii.unhexlify(APP_EUI)
    app_key = binascii.unhexlify(APP_KEY)

    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
    i = 0
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        i = i + 2.5
        print('Not yet joined after ' + str(i)+"s ... ")

    print('Joined.')
    pycom.rgbled(YELLOW) # red


# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)
######################
