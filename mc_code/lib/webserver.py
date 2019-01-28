from microWebSrv import MicroWebSrv
from network import WLAN
from time import sleep
import sys

class Webserver():

    def __init__(self, dev_state):
        self.wlan = None
        self.mws = MicroWebSrv(webPath='www/')
        self.dev_state = dev_state

    def start(self):
        print('Start wlan access point and webserver.')
        self.wlan = WLAN(mode=WLAN.AP, ssid="GEWV_LORA_NODE_" + self.dev_state.dev_eui, auth=(WLAN.WPA2, "let_me_in"), channel=7, antenna=WLAN.INT_ANT)
        self.mws.Start()
        sleep(0.2)

        if self.mws.IsStarted():
            print('Webserver is started.')
        else:
            raise Exception('Webserver start failed.')

    def stop(self):
        print('Stop wlan and webserver.')
        self.mws.Stop()
        if self.wlan: self.wlan.deinit()

        if not self.mws.IsStarted():
            print('Webserver and wlan is stopped.')
        else:
            raise Exception('Webserver stop is failed.')

    def init_webserver(self):
        def httpHandlerGETState(httpClient, httpResponse):
            httpResponse.WriteResponseJSONOk(   headers = None,
                                                obj = self.dev_state.get_state())

        def httpHandlerPOSTsearchOnewire(httpClient, httpResponse):
            if self.dev_state.onewire_interface is not None:
                try:
                    print('Request new search for one wire devices.')
                    one_wire_inf = self.dev_state.onewire_interface
                    one_wire_inf.interfacereset()
                    one_wire_inf.getallid()
                    one_wire_inf.checkdevices()

                    self.dev_state.clear_sensors()
                    one_wire_inf.update_state(self.dev_state)

                    print('Find {} devices.'.format(one_wire_inf.num_devices))
                    res = { "numDevices": one_wire_inf.num_devices }
                    httpResponse.WriteResponseJSONOk(   headers = None,
                                                        obj = res)
                except Exception as e:
                    sys.print_exception(e)
                    httpResponse.WriteResponseBadRequest()
            else:
                httpResponse.WriteResponseBadRequest()


        self.routeHandlers = [
            ( '/state', 'GET', httpHandlerGETState),
            ( '/search_onewire', 'POST', httpHandlerPOSTsearchOnewire)
        ]

        self.mws = MicroWebSrv(
            webPath='www/',
            routeHandlers=self.routeHandlers )
