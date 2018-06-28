#from time import sleep
from ds2480b import *

def printid(array):
    "print sensor id in hex"
    i = 0
    for i in range(0, len(array)):
        print(hex(array[i]))

print('*******************Testprogramm DS2480B************************')
VAR = DS2480b(DEBUG=1)
VAR.initrs232(1)

print("search...")
VAR.getallid()
VAR.debug = 1
clientno = VAR.checkdevices()
VAR.debug = 0
for i in range(0, 1000):
    VAR.converttemp()
    print("Abfrage " + str(i) + ": ")
    for j in range(0, clientno-1):
        printid(VAR.romstorage[j])
        print(VAR.acquiretemp(j))
        print("'C'")
    #sleep(1)

VAR.closers232()

#print hex(VAR.Temperature)

#print var.temperature
