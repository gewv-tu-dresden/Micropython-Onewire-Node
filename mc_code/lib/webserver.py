from microWebSrv import MicroWebSrv
from network import WLAN
from time import sleep

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
        self.wlan.deinit()

        if not self.mws.IsStarted():
            print('Webserver and wlan is stopped.')
        else:
            raise Exception('Webserver stop is failed.')

    def init_webserver(self):
        def httpHandlerGETState(httpClient, httpResponse):
            httpResponse.WriteResponseJSONOk(   headers = None,
                                                obj = self.dev_state.get_state())

        def httpHandlerGETChartist(httpClient, httpResponse):
            print('Chartist is requested.')
            httpResponse.WriteResponseFile('chartist.min.js',
                                           contentType='application/javascript',
                                           headers=None)

        self.routeHandlers = [
            ( '/state', 'GET', httpHandlerGETState),
            ( '/chartist.min.js', 'GET', httpHandlerGETChartist)
        ]

        self.mws = MicroWebSrv(
            webPath='www/',
            routeHandlers=self.routeHandlers )
