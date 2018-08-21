class State():

    def __init__(self):
        self.dev_eui = None
        self.app_eui = None
        self._app_key = None
        self.sensors = {}

    @property
    def app_key(self):
        return None

    @app_key.setter
    def app_key(self, value):
        self._app_key = value

    def add_sensor(self, id, name, last_value=None):
        self.sensors[id] = [name, last_value]

    def update_sensor(self, id, value):
        self.sensors[id][1] = value

    def remove_sensor(self, id):
        del self.sensors[id]

    def get_state(self):
        return {
            "dev_eui": self.dev_eui,
            "app_eui": self.app_eui,
            "sensors": self.sensors,
        }
