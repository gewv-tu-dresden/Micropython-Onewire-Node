from machine import Timer

HISTORY_SIZE = 50

class State():

    def __init__(self):
        self.dev_eui = None
        self.app_eui = None
        self._app_key = None
        self.onewire_interface = None
        self.chrono = Timer.Chrono()
        self.chrono.start()
        self.sensors = {}

    @property
    def app_key(self):
        return None

    @app_key.setter
    def app_key(self, value):
        self._app_key = value

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
