from machine import UART
from copy import deepcopy
from binascii import unhexlify

__license__ = "IEEH 2018"
__revision__ = " 05_2018 "

class DS2480b(object):
    """one wire master DS2480b Abfrage"""
    #lokale Konstanten
    #declare konstanten DS2480b
    # uart.write() nur mit bytebuffer möglich
    # am besten nur umwandeln, wenn notwendig
    __ACK = b'\xCD'
    __RESET = b'\xC1'
    __PULLUP = b'\x3B'
    __DATAMODE = b'\xE1'
    __COMMANDMODE = b'\xE3'
    __PULLUPARM = b'\xEF'
    __PULLUPDISARM = b'\xED'
    __PULSETERMINATE = b'\xF1'
    __PULLUPDISARM = b'\xED'
    __SEARCHROM = b'\xF0'
    __ACCELERATORON = b'\xB1'
    __ACCELERATOROFF = b'\xA1'
    #declare konstanten DS1820
    __CONVERTT = '44'
    __READ = 'BE'
    __SKIPROM = 'CC'
    __MATCHROM = '55'
    #delacre variabeln fuer die Klasse
    _iscmdmode = 0
    #search state
    _lastdiscrepancy = 0
    _lastdeviceflag = False
    _lastfamilydiscrepancy = 0
    newromno = [0]*8

    #variabeln der Klasseserial
    def __init__(self, TEMPERATURE=0, DS1920NO=0, DS1920FIRST=0, DS19B20NO=0,
    DS19B20FIRST=0, ROMSTORAGE=[None]*100, INTERFACE="", DEBUG=0):
        #init der methoden variabeln"
        self.temperature = TEMPERATURE
        self.ds1920no = DS1920NO
        self.ds1920first = DS1920FIRST
        self.ds19b20no = DS19B20NO
        self.ds19b20first = DS19B20FIRST
        self.romstorage = ROMSTORAGE
        self.interface = INTERFACE
        self.debug = 1

#******************RS232 Routinen***********************************************
    def interfacereset(self):
        """reset interface"""
        print("Err UART --> Reset Interface")
        self.interface.close()
        self.interface.open()
        self.portwrite(self.__RESET)

    def initrs232(self, port=1, baud=9600):
        """Init RS232"""
        self.interface = UART(port, baud)
        self.interface.init(baud)
        #if self.interface.open:
        #    print('open:'+value)
        #    print(self.interface)
        #else:str(
        #    print("Err RS232 Init")

    def closers232(self):
        """port schliessen"""
        name = self.interface.name
        self.interface.deinit()
        print(name + " close")

    def getchrrs232(self):
        """Rx char"""
        result = self.interface.read(1)
        if result is not None:
            if self.debug == 1:
                print("debug ASCII in: ")
                for i in range(0, len(result)):
                    print("{} hex: {}".format(result[i], hex(result[i])))

            return result[0]
        else:
            return 0

    def flushrs232(self, value=100):
        """clear input buffer"""
        for i in range(0, value):
            self.getchrrs232()


#*********************DS2480B Routinen******************************************
    def commandmode(self):
        """check commandmode"""
        if self._iscmdmode == 0:
            self._iscmdmode = True
            self.portwrite(self.__COMMANDMODE)
            return self.getchrrs232()


    def datamode(self):
        """check datamode"""
        if self._iscmdmode == 1:
            self._iscmdmode = False
            self.portwrite(self.__DATAMODE)

    def portwrite(self, value=0):
        """write data"""
        if self.debug == 1:
            # print("debug value write:" + hex(value))
            print("debug value raw:" + str(value))
            print("debug value bytes:" + str(unhexlify(value)))

        self.interface.write(unhexlify(value))
        if self._iscmdmode == 1:
            return self.getchrrs232()

    def writebit(self, value=0, waitforreply=1):
        """Write a bit - actually returns the bit read back in case you care."""
        getchr = 0
        self.commandmode()
        #if self.debug == 1:
        #    print "writebit: " + bin(value)
        if value == 1:
            getchr = self.portwrite(0x91) #write a single "on" bit to onewire
        else:
            getchr = self.portwrite(0x81) #write a single "off" bit to onewire
        if waitforreply == 1:
            return getchr & 1

    def readbit(self):
        """Read a bit - short hand for writing a 1 and seeing what we get back."""
        return self.writebit(1)

    def writemode(self, value=0):
        """Tx UART value without return from DS2480b"""
        if self.debug == 1:
            print("debug value write:" + hex(value))
        self.interface.write([value])

    def writecommand(self, value=0):
        """Tx UART value with return from DS2480b"""
        self.commandmode()
        self.interface.write([value])
        result = self.getchrrs232()
        return result

    def reset(self):
        """reset one wire bus"""
        self.commandmode()
        char = self.portwrite(self.__RESET)
        if char == self.__ACK:
            return 1
        else:
            self.interfacereset()
            return 0

    def resetsearch(self, clearrom=0):
        """reset the search state"""
        self._lastdiscrepancy = 0
        self._lastdeviceflag = False
        self._lastfamilydiscrepancy = 0
        if clearrom == 1:
            self.newromno = [0]*8

    def search(self):
        """
        // Perform a search. If this function returns a '1' then it has
        // enumerated the next device and you may retrieve the ROM from the
        // DS2480B::address variable. If there are no devices, no further
        // devices, or something horrible happens in the middle of the
        // enumeration then a 0 is returned.  If a new device is found then
        // its address is copied to newAddr.  Use DS2480B::reset_search() to
        // start over.newromno
        //
        // --- Replaced by the one from the Dallas Semiconductor web site ---
        //-------------------value-------------------------------------------------------
        // Perform the 1-Wire Search Algorithm on the 1-Wire bus using the existing
        // search state.
        // Return TRUE  : device found, ROM number in ROM_NO buffer
        //        FALSE : device not found, end of search
        """
        ##initialize for search
        id_bit_number = 1
        last_zero = 0
        rom_byte_number = 0
        rom_byte_mask = 1
        search_result = 0

        id_bit = False
        cmp_id_bit = False
        search_direction = False

        if self.debug == 1:
            print("search allgorithm")
        #if the last call was not the last one
        if self._lastdeviceflag == 0:
            if self.reset() == 0:
                self.resetsearch()
                return False
            self.datamode()
            self.portwrite(self.__SEARCHROM)
            self.getchrrs232()
            while True:
                #read a bit and its complement
                id_bit = self.readbit()
                cmp_id_bit = self.readbit()
                #if self.debug == 1:
                    #print "####bit read: " + bin(id_bit) +" comp: "+ bin(cmp_id_bit)
                #check for no devices on 1-wire
                if (id_bit == 1)and(cmp_id_bit == 1):
                    break
                else:
                    #all devices coupled have 0 or 1
                    if id_bit != cmp_id_bit:
                        search_direction = id_bit #bit write value for search
                    else:
                    #if this discrepancy if before the Last Discrepancy
                    # on a previous next then pick the same as last time
                        if id_bit_number < self._lastdinewromnoscrepancy:
                            search_direction = ((self.newromno[rom_byte_number] & rom_byte_mask) > 0)

                        else:
                            #if equal to last pick 1, if not then pick 0
                            search_direction = (id_bit_number == self._lastdiscrepancy)
                        #if 0 was picked then record its position in LastZero
                        if search_direction == 0:
                            last_zero = id_bit_number
                            #check for Last discrepancy in family
                            if last_zero < 9:
                                self._lastfamilydiscrepancy = last_zero
                #set or clear the bit in the ROM byte rom_byte_number
                # with mask rom_byte_mask
                if search_direction == 1:
                    self.newromno[rom_byte_number] |= rom_byte_mask
                else:
                    self.newromno[rom_byte_number] &= ~rom_byte_mask
                #serial number search direction write bit
                self.writebit(search_direction)
                #increment the byte counter id_bit_number
                #and shift the mask rom_byte_mask
                id_bit_number += 1
                rom_byte_mask <<= 1
                #if the mask is 0 then go to new SerialNum
                #byte rom_byte_number and reset mask
                if rom_byte_mask >= 0xff:
                    rom_byte_number += 1
                    rom_byte_mask = 1
                #loop until through all ROM bytes 0-7
                if rom_byte_number == 8:
                    break
            #if the search was successful then
            if (id_bit_number < 65) == 0:
                #search successfulself.getchrrs232()
                #so set LastDiscrepancy,LastDeviceFlag,search_result
                self._lastdiscrepancy = last_zero
                #check for last device
                if self._lastdiscrepancy == 0:
                    self._lastdeviceflag = True
                search_result = True
        #if no device found then reset counters
        #so next 'search' will be like a first
        if search_result == 0 or self.newromno[0] == 0:
            search_result = False
        else:
            for i in range(0, 8):
            #newAddr[i] = self.newromno[i]
                if self.debug == 1:
                    print(hex(self.newromno[i]))
            if self.debug == 1:
                print(" ")
        return search_result

    def getallid(self):
        """get all one wire id's"""
        i = 0
        j = 0
        while True:
            if self.search() == 0:
                break
            if self.crc8(self.newromno) == 0:
                self.romstorage[i] = deepcopy(self.newromno)
                i += 1
            else:
                if self.debug == 1:
                    print("ERR CRC8 Test")
        if self.debug == 1:
            i = 0
            print(" ")
            while self.romstorage[i] != None:
                print("{}:   ".format(str(i)))
                for j in range(0, len(self.romstorage[i])):
                    print(hex(self.romstorage[i][j]), end="")
                i += 1
                print(" ")
        return self.romstorage

    def crc8(self, data):
        """Compute CRC"""
        crc = 0
        for i in range(len(data)):
            byte = data[i]
            for j in range(8):
                fb_bit = (crc ^ byte) & 0x01
                if fb_bit == 0x01:
                    crc = crc ^ 0x18
                crc = (crc >> 1) & 0x7f
                if fb_bit == 0x01:
                    crc = crc | 0x80
                byte = byte >> 1
        return crc

#**********************DS18x20 Routinen*****************************************
    def converttemp(self):
        """DS1820 Temp.messung anstossen"""
        result = 0
        self.commandmode()
        self.portwrite(self.__PULLUP)
        if self.reset() == 1:
            self.datamode()
            self.portwrite(self.__SKIPROM)
            self.commandmode()
            self.portwrite(self.__PULLUPARM)
            self.portwrite(self.__PULSETERMINATE)
            self.datamode()
            self.portwrite(self.__CONVERTT)
            result = self.getchrrs232()
            self.commandmode()
            self.portwrite(self.__PULLUPDISARM)
            self.portwrite(self.__PULSETERMINATE)
            self.getchrrs232()
            self.reset()
        return result

    def acquiretemp(self, adress):
        """DS1820 aktuelle Temperatur abfragen"""
        scratchpad = [None]*9
        if self.debug == 1:
            print("gettemp")
        if self.reset() == 1:
            self.datamode()
            self.portwrite(self.__MATCHROM)
            self.getchrrs232()
            for i in range(0, 8):
                self.portwrite(self.romstorage[adress][i])
                if self.debug == 1:
                    print(hex(self.romstorage[adress][i]), end="")
            self.portwrite(self.__READ)
            self.flushrs232(9)
            dummy = [0] * 8
            for i in range(0, 9):
                self.portwrite(0xff)
                scratchpad[i] = self.getchrrs232()
            self.commandmode()
            self.reset()
            if self.crc8(scratchpad) != 0:
                self.temperature = 9999.999
                return self.temperature
            #calculate temperatur
            #ds1820
            if self.romstorage[adress][0] == 0x10:
                integer = 0
                for i in range(1, -1, -1):
                    integer = integer * 256 + scratchpad[i]
                integer = integer / 2
                self.temperature = ((scratchpad[7] - scratchpad[6]) / scratchpad[7]) + integer - 0.25
            #ds18b20
            if self.romstorage[adress][0] == 0x28:
                integer = 0
                for i in range(1, -1, -1):
                    integer = integer * 256 + scratchpad[i]
                self.temperature = (integer * 25.0) / 400.0
        return self.temperature

    def checkdevices(self):
        """count onewire slaves"""
        devices = 0
        kind = 0
        self.ds1920no = 0
        self.ds1920first = 0
        self.ds19b20no = 0
        self.ds19b20first = 0
        if self.debug == 1:
            print("get sensor type")
        for i in range(0, len(self.romstorage)):
            devices += 1
            #check nesty value
            if self.romstorage[i] == None:
                break
            #mask of lsb
            kind = self.romstorage[i][0]
            if self.debug == 1:
                print("kind:" + hex(kind))
            if kind == 0x10:
                if self.ds1920no == 0:
                    self.ds1920first = i
                    if self.debug == 1:
                        print("first ds1920:" + hex(i))
                self.ds1920no += 1
            if kind == 0x28:
                if self.ds19b20no == 0:
                    self.ds19b20first = i
                    if self.debug == 1:
                        print("first ds19b20:" + hex(i))
                self.ds19b20no += 1
        return devices
