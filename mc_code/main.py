#from time import sleep
from ds2480b import *
from machine import Pin

#'config IO'
myled = Pin('P2', mode=Pin.OUT)
myswitch = Pin('P8', mode=Pin.IN, pull=Pin.PULL_UP)

myled.value(1)

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
j=0
i=0
go = 1
riegel = 1
while (1):
    myled.toggle()
    sleep(0.2)
    if myswitch()==0 and riegel ==1:
        print ('Taster')
        riegel = 0
        if go == 1:
            print('Abfrage AUS')
            go = 0
        else:
            print('Abfrage EIN')
            go = 1
    if myswitch()==1 and riegel ==0:
        riegel = 1
    if go == 1:
        i+=1
        VAR.converttemp()
        print("Abfrage " + str(i) + ": ")
        sleep(0.8)
        for j in range(0, clientno-1):
            print(VAR.romstorage[j], end="")
            print(VAR.acquiretemp(j), end="")
            print("'C'")
VAR.closers232()
