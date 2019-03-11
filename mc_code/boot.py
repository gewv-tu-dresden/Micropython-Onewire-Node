import machine
import os
import time
import ubinascii as binascii
import pycom
import json
from machine import WDT
from network import LoRa
import socket
from webserver import Webserver
from state import State
from utils import log
from sender import Sender

# Initialize Uart
uart = machine.UART(
    0, 115200)  # disable these two lines if you don't want serial access
os.dupterm(uart)

# == Load environment == #
if 'env.json' in os.listdir():
    # load the file in a seperate Array
    f = open('env.json', 'r')
    env = json.load(f)
    print('Env Variables: \n {}'.format(env))
    f.close()
else:
    raise Exception("No environment file.")

# == Const == #
RED = 0x220000
YELLOW = 0x222200

# state of the system
state = State()
state.app_eui = '0000000000000000'

# Node_1
state.dev_eui = env['dev_eui']
state.app_key = env['app_key']

# LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# Initialize watchdog
wdt = WDT(timeout=1500000)

# Initialize Webserver
wser = Webserver(dev_state=state)
wser.init_webserver()

####################

pycom.heartbeat(False)
pycom.rgbled(RED)

# == Configure Lora == #
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
    dev_eui = binascii.unhexlify(state.dev_eui)
    app_eui = binascii.unhexlify(state.app_eui)
    app_key = binascii.unhexlify(state._app_key)

    # join a network using OTAA (Over the Air Activation)
    lora.join(
        activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
    i = 0
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        i = i + 2.5
        print('Not yet joined after ' + str(i) + "s ... ")

    print('Joined.')
    pycom.rgbled(YELLOW)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)

# init Sender module
sender = Sender(state=state, lora_socket=s)

######################
