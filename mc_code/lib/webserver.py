from microWebSrv import MicroWebSrv
from network import WLAN
from time import sleep, time
import sys
from utils import log

class Webserver():

    def __init__(self, dev_state):
        self.wlan_agent = dev_state.wlan_agent
        self.mws = MicroWebSrv(webPath='www/')
        self.dev_state = dev_state

    def start(self):
        log('Start webserver.')
        if not self.wlan_agent.isActive():
            raise Exception("Cant start webserver without wlan.")

        self.mws.Start()

        now = time()
        while not self.mws.IsStarted():
            sleep(0.1)
            if (time()-now > 10):
                raise Exception('Webserver start is failed.')

        log('Webserver is started.')

    def stop(self):
        log('Stop webserver.')
        self.mws.Stop()

        now = time()
        while self.mws.IsStarted():
            sleep(0.1)
            if (time()-now > 10):
                raise Exception('Webserver stop is failed.')

        log('Webserver is stopped.')

    def init_webserver(self):
        def httpHandlerGETState(httpClient, httpResponse):
            httpResponse.WriteResponseJSONOk(   headers = None,
                                                obj = self.dev_state.get_state())

        def httpHandlerPOSTsearchOnewire(httpClient, httpResponse):
            if self.dev_state.onewire_interface is not None:
                try:
                    log('Request new search for one wire devices.')
                    one_wire_inf = self.dev_state.onewire_interface
                    one_wire_inf.interfacereset()
                    one_wire_inf.getallid()
                    one_wire_inf.checkdevices()

                    self.dev_state.clear_sensors()
                    one_wire_inf.update_state(self.dev_state)

                    log('Find {} devices.'.format(one_wire_inf.num_devices))
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
