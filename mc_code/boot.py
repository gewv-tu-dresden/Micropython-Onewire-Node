import machine
import os
import time
import ubinascii as binascii
import pycom
import json
from machine import WDT
from network import LoRa
from wlan import WLANAgent
import socket
from state import State
from sender import Sender

# Initialize Uart
uart = machine.UART(0, 115200)
# disable these two lines if you don't want serial access
os.dupterm(uart)

# == Load environment == #
if "env.json" in os.listdir():
    # load the file in a seperate Array
    f = open("env.json", "r")
    env = json.load(f)
    print("Env Variables: \n {}".format(env))
    f.close()
else:
    raise Exception("No environment file.")

# == Const == #
RED = 0x220000
YELLOW = 0x222200

# Init Wifi Agent
ap_config = env["wlan_ap"]
sta_config = env["wlan_sta"]
wlan_agent = WLANAgent(ap_config=ap_config, sta_config=sta_config)

# state of the system
state = State(wlan_agent=wlan_agent)

# Node_1
state.dev_eui = env["dev_eui"]
state.app_key = env["app_key"]
state.app_eui = env["app_eui"]
state.deepsleep = env.get('deepsleep', True)

# LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
lora.nvram_restore()

# Initialize watchdog
wdt = WDT(timeout=1500000)

####################

pycom.heartbeat(False)
pycom.rgbled(RED)

# == Configure Lora == #
print("Resetcause {}".format(machine.reset_cause()))

if lora.has_joined():
    print("Skipping joining.")
else:
    print("Try to join TTN")
    # create an OTAA authentication parameters
    dev_eui = binascii.unhexlify(state.dev_eui)
    app_eui = binascii.unhexlify(state.app_eui)
    app_key = binascii.unhexlify(state._app_key)

    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
    i = 0
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        i = i + 2.5
        print("Not yet joined after " + str(i) + "s ... ")

    print("Joined.")
    pycom.rgbled(YELLOW)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)

# init Sender module
http_config = env.get("http_interface")
sender = Sender(
    state=state,
    lora_socket=s,
    http_config=http_config,
    wlan_agent=wlan_agent,
    default_unit="°C",
)

######################
