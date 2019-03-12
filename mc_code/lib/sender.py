from cayennelpp import CayenneLPP
from utils import debug, log, zfill
from state import RF_MODES
from requests import post

class Sender:

    def __init__(self, state, lora_socket=None, http_config=None, wlan_agent=None):
        self._state = state
        self._lora_socket = lora_socket
        self._lora_buffer = CayenneLPP(size=51, sock=self._lora_socket)
        self._http_buffer = self.build_basic_http_payload()
        self._http_config = http_config
        if self._http_config is not None:
            self._http_url = self._http_config['url']

        self._wlan_agent = wlan_agent

    def build_basic_http_payload(self):
        return {
            "sender_id": "radio_module_01",
            "datapoints": []
        }

    def send_items(self):
        if self._state.rf_mode == RF_MODES.LORA:
            log("Send temps to lora server.")
            debug("Payloadsize: {}".format(self._lora_buffer.get_size()), self._state.debug_mode)
            self._lora_buffer.send(reset_payload=True)
        elif self._http_config is not None and (self._state.rf_mode == RF_MODES.WLAN_AP or self._state.rf_mode == RF_MODES.WLAN_CLIENT):
            try:
                log("Send temps to http server.")
                res = post(self._http_url, json=self._http_buffer)
                log("Succed to send data to http server. Status: {} Response: {}".format(res.status_code, res.reason))
            except ValueError:
                log('Host url seems to be incorrect.')
                raise
            except OSError as err:
                # err == -1 -> no connection
                # err == [Errno 104] ECONNRESET
                log('Error by sending message to http server.')
                log(err)
            except Exception as exc:
                log('Unknown error by sending message to http server.')
                log(exc)

            self._http_buffer = self.build_basic_http_payload()
        else:
            debug("Send no data, because wrong rf mode.", self._state.debug_mode)


    def add_temperature(self, value, channel):
        if self._state.rf_mode == RF_MODES.LORA:
            self._lora_buffer.add_temperature(value, channel)
        elif self._state.rf_mode == RF_MODES.WLAN_AP or self._state.rf_mode == RF_MODES.WLAN_CLIENT:
            self._http_buffer['datapoints'].append({
                "label": "temperature_sensor_" + zfill(channel, 3),
                "unit": "celsius",
                "quantity": value
            })
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)

    def is_within_size_limit(self, size):
        if self._state.rf_mode == RF_MODES.LORA:
            return self._lora_buffer.is_within_size_limit(size)
        elif self._state.rf_mode == RF_MODES.WLAN_AP or self._state.rf_mode == RF_MODES.WLAN_CLIENT:
            return True
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)

    def get_size(self):
        if self._state.rf_mode == RF_MODES.LORA:
            return self._lora_buffer.get_size()
        elif self._state.rf_mode == RF_MODES.WLAN_AP or self._state.rf_mode == RF_MODES.WLAN_CLIENT:
            return len(list(self._http_buffer.items()))
        else:
            debug("Not implemented rf mode.", self._state.debug_mode)
