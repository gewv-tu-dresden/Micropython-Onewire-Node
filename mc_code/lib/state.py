from machine import Timer
from machine import Pin
from button import Button
from pycom import rgbled


HISTORY_SIZE = 50
RGBOFF = 0x050505
MEASURING_COLOR = 0x007f00
NO_MEASURING_COLOR = 0x7f0000
TOGGLE_MEASURING_COLOR = 0x7f7f00
TOGGLE_DEBUG_COLOR = 0x007f7f

class RF_MODES():
    NO_MODE = "NO_MODE"
    WLAN_AP = "WLAN_AP"
    WLAN_CLIENT = "WLAN_CLIENT
    LORA = "LORA"

class State():

    def __init__(self):
        self.dev_eui = None
        self.app_eui = None
        self.rf_mode = None
        self.measuring_mode = True
        self.debug_mode = False
        self._app_key = None
        self.onewire_interface = None
        self.web_server = None
        self.chrono = Timer.Chrono()
        self.chrono.start()
        self.sensors = {}
        self.rgb_color = 0x007f00
        self.case_button = Button('P8', longms=500)

        # init pins for mode recognizion
        self.bin_switch_1 = Pin('P10', mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.bin_switch_2 = Pin('P11', mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.bin_switch_3 = Pin('P12', mode=Pin.IN, pull=Pin.PULL_DOWN)

        trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING
        self.update_node_mode()
        self.bin_switch_1.callback(trigger, self.update_node_mode)
        self.bin_switch_2.callback(trigger, self.update_node_mode)
        self.bin_switch_3.callback(trigger, self.update_node_mode)

        self.case_button.short = self.toggle_measuring
        self.case_button.long = self.toggle_debug

    @property
    def app_key(self):
        return None

    # helper functions
    def set_rgb_color(color):
        """change local led colour"""
        self.rgb_color = color
        rgbled(color)

    def update_node_mode(arg):
        # pin 1 and 2          0 0        0 1          1 0        1 1
        # possible rf mode ["NO_MODE", "WLAN_AP", "WLAN_CLIENT", "LORA"]
        # measuring mode pin 3
        switch_1 = self.bin_switch_1()
        switch_2 = self.bin_switch_2()
        switch_3 = self.bin_switch_3()

        if switch_1 and switch_2:
            self.rf_mode = RF_MODES.LORA
        else if switch_1 and not switch_2:
            self.rf_mode = RF_MODES.WLAN_CLIENT
        else if not switch_1 and switch_2:
            self.rf_mode = RF_MODES.WLAN_AP
        else:
            self.rf_mode = RF_MODES.NO_MODE

        # self.measuring_mode = switch_3

    @app_key.setter
    def app_key(self, value):
        self._app_key = value

    def toggle_debug():
        rgbled(TOGGLE_DEBUG_COLOR)
        self.debug_mode = not self.debug_mode

        if self.onewire_interface is not None:
            self.onewire_interface.debug = self.debug_mode

        sleep(0.5)
        rgbled(self.rgb_color)

    def toggle_measuring():
        rgbled(TOGGLE_MEASURING_COLOR)
        self.measuring_mode = not self.measuring_mode

        if self.measuring_mode:
            log('Measuring on')
            self.set_rgb_color(MEASURING_COLOR)
        else:
            log('Measuring off')
            self.set_rgb_color(NO_MEASURING_COLOR)

    def add_sensor(self, id, name, last_value=None):
        timestamp = self.chrono.read()
        counter = 0
        self.sensors[id] = [name, last_value, timestamp, counter, [None]*HISTORY_SIZE]

    def update_sensor(self, id, value):
        counter = self.sensors[id][3]
        self.sensors[id][4][counter] = [self.sensors[id][1], self.sensors[id][2]]

        if counter == HISTORY_SIZE-1:
            counter = 0
        else:
            counter += 1

        self.sensors[id][1] = value
        self.sensors[id][2] = self.chrono.read()
        self.sensors[id][3] = counter

    def remove_sensor(self, id):
        del self.sensors[id]

    def clear_sensors(self):
        self.sensors = {}

    def get_state(self):
        return {
            "dev_eui": self.dev_eui,
            "app_eui": self.app_eui,
            "sensors": self.sensors,
            "send_time": self.chrono.read()
        }
