from cayennelpp import CayenneLPP
from utils import debug, log
from state import RF_MODES

class Sender:

    def __init__(self, state, lora_socket):
        self._state = state
        self._lora_socket = lora_socket
        self._lora_buffer = CayenneLPP(size=51, sock=self._lora_socket)

    def send_items(self):
        if self._state.rf_mode == RF_MODES.LORA:
            log("Send temps to app server.")
            debug("Payloadsize: {}".format(self._lora_buffer.get_size()), self._state.debug_mode)
            self._lora_buffer.send(reset_payload=True)
        else:
            debug("Send no data, because wrong rf mode.", self._state.debug_mode)

        self._lora_buffer.reset_payload()


    def add_temperature(self, value, channel):
        if self._state.rf_mode == RF_MODES.LORA:
            self._lora_buffer.add_temperature(value, channel)
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)

    def is_within_size_limit(self, size):
        if self._state.rf_mode == RF_MODES.LORA:
            return self._lora_buffer.is_within_size_limit(size)
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)

    def get_size(self):
        if self._state.rf_mode == RF_MODES.LORA:
            return self._lora_buffer.get_size()
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)
