#from time import sleep
from ds2480b import *
from machine import Pin
from cayennelpp import CayenneLPP

#'config IO'
myled = Pin('P2', mode=Pin.OUT)
switch1 = Pin('P8', mode=Pin.IN, pull=Pin.PULL_UP)
switch2 = Pin('P23', mode=Pin.IN, pull=Pin.PULL_UP)
myled.value(1)

# Cayenne LowPowerPayload
c = CayenneLPP()

def printid(array):
    "print sensor id in hex"
    i = 0
    for i in range(0, len(array)):
        print(hex(array[i]))

print('*******************Testprogramm DS2480B************************')
VAR = DS2480b()
VAR.initrs232(1)

print("search...")
VAR.getallid()
VAR.debug = 1
clientno = VAR.checkdevices()
VAR.debug = 0

go = 1
riegel = 1
turns = 0

while (1):
    myled.toggle()
    sleep(0.2)

    # only every 30 reads a package should send
    sendThisTurn = i % 30 == 0

    if switch1()==0 and riegel ==1:
        print('switch1')
        riegel = 0
        if go == 1:
            print('Abfrage AUS')
            go = 0
        else:
            print('Abfrage EIN')
            go = 1

    if switch1()==1 and riegel ==0:
        riegel = 1

    if go == 1:
        i+=1
        VAR.converttemp()
        print("Abfrage " + str(i) + ": ")
        sleep(0.8)
        for j in range(0, clientno-1):
            rom_storage = VAR.romstorage[j]
            acq_temp = VAR.acquiretemp(j)

            # only every 30 reads a package should send
            if sendThisTurn:
                c.addTemperature(j, acq_temp)

            print("{} {} 'C'".format(rom_storage, acq_temp))

    if switch2()==0:
        print("switch2")
        break

    if sendThisTurn:
        print("Send temps to app server.")
        s.setblocking(True)
        s.send(c.getBuffer())
        s.setblocking(False)

VAR.closers232()
