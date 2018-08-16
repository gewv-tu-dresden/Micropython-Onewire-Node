import machine
import os
import time
import ubinascii as binascii
import pycom
from machine import WDT
from network import LoRa, WLAN
import socket
from microWebSrv import MicroWebSrv

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

# Initialize wlan access point
wlan = WLAN(mode=WLAN.AP, ssid="GEWV_LORA_NODE_" + DEV_EUI, auth=(WLAN.WPA2, "let_me_in"), channel=7, antenna=WLAN.INT_ANT)

@MicroWebSrv.route('/test')
def httpHandlerTestGet(httpClient, httpResponse):
    content = """
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = {}
            <br />
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                First name: <input type="text" name="firstname"><br />
                Last name: <input type="text" name="lastname"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """.format(httpClient.GetIPAddr())

    httpResponse.WriteResponseOk(   headers = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = content )

@MicroWebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname  = formData["lastname"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
    """ % ( MicroWebSrv.HTMLEscape(firstname),
            MicroWebSrv.HTMLEscape(lastname) )
    httpResponse.WriteResponseOk( headers         = None,
                                  contentType     = "text/html",
                                  contentCharset = "UTF-8",
                                  content          = content )


@MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
    """
    content += "<h1>EDIT item with {} variable arguments</h1>"\
        .format(len(args))

    if 'index' in args :
        content += "<p>index = {}</p>".format(args['index'])

    if 'foo' in args :
        content += "<p>foo = {}</p>".format(args['foo'])

    content += """
        </body>
    </html>
    """
    httpResponse.WriteResponseOk( headers         = None,
                                  contentType     = "text/html",
                                  contentCharset = "UTF-8",
                                  content          = content )
# Initialize Webserver
mws = MicroWebSrv(webPath='www/')
mws.Start()

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
