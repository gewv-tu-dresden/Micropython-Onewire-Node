from time import sleep
from ds2480b import *
from machine import Pin
import machine
from cayennelpp import CayenneLPP

#'config IO'
switch1 = Pin('P8', mode=Pin.IN, pull=Pin.PULL_UP)

#prüfen ob exclude.dat auf dem lopy4 vorhanden ist
if 'exclude.dat' in os.listdir():
    #laden der datei und in ein sep. Array speichern
    f = open('exclude.dat',"r")
    exclude = f.read()
    print ('{} ausgeschlossene Sensoren'.format(exclude))
    exclude = exclude.split(';')
    f.close()
else:
    #erzeugen der datei
    f = open('exclude.dat', 'w')
    exclude = ("-1;")
    f.write(exclude)
    print ("init file 'exclude.dat'@"+exclude)
    exclude = exclude.split(";")
    f.close()


def printid(array):
    "print sensor id in hex"
    i = 0
    for i in range(0, len(array)):
        print(hex(array[i]))
def senditems():
    "send temps"
    print("Send temps to app server.")
    print("Payloadsize: {}".format(lpp.get_size()))
    lpp.send(reset_payload=True)

print('*******************Testprogramm DS2480B************************')
VAR = DS2480b()
VAR.initrs232(1)

print("search... please wait... ;-)")
VAR.getallid()

#VAR.debug = 1
clientno = VAR.checkdevices()
print ("find {}x DS19B20 Sensor and {}x DS1920 Sensor".format(VAR.ds19b20no, VAR.ds1920no))
#VAR.debug = 0

print("initialize cayennelpp")
lpp = CayenneLPP(size=64, sock=s)

go = 1
riegel = 1
turns = 0
i = 0
err_count = [0]*len(VAR.romstorage)


while (1):
    sleep(0.8)

    # only every 30 reads a package should send
    sendThisTurn = 0

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
        if (VAR.ds19b20no == 0 and VAR.ds1920no == 0):
            VAR.getallid()
        print("Abfrage " + str(i) + ": ")
        VAR.converttemp()
        for j in range(0, clientno-1):
            #if exclude.find(str(j)) != -1:
            if (str(j) in exclude):
                print ("fehlerhaften Sensor No.{} übersprungen".format(j+1))
                continue
            rom_storage = VAR.romstorage[j]
            acq_temp = VAR.acquiretemp(j)

            #Anpassung onewire Ring --> defekte Sensoren???
            if VAR.resetflag == 0:
                err_count[j] = err_count[j] + 1
                print ('Sensor No. {} --> Reset Err {}'.format(j+1,err_count[j]))
                if err_count[j] == 5:
                    print("Err No.{} TempSensor: {}".format(j+1, rom_storage))
                    f = open("exclude.dat", "a+")
                    f.write(str(j)+";")
                    f.close()
                    machine.reset()
            else:
                err_count[j] = 0
                lpp.add_temperature(acq_temp, j)
                if not lpp.is_within_size_limit(2):
                    senditems()
                print("{}:{} {} 'C'".format(j+1, rom_storage, acq_temp))
        if lpp.get_size():
            senditems()
        sleep(4.2)
VAR.closers232()
