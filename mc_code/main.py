#from time import sleep
from ds2480b import *

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
for i in range(0, 50):
    VAR.converttemp()
    sleep(2)
    print("Abfrage " + str(i) + ": ")
    for j in range(0, clientno-1):
        print(VAR.romstorage[j], end="")
        print(VAR.acquiretemp(j), end="")
        print("'C'")
VAR.closers232()