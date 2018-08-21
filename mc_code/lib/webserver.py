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
        self.wlan = WLAN(mode=WLAN.AP, ssid="GEWV_LORA_NODE_" + self.dev_state['dev_eui'], auth=(WLAN.WPA2, "let_me_in"), channel=7, antenna=WLAN.INT_ANT)
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
        def httpHandlerTestGet(httpClient, httpResponse):
            # TODO: Need self here. But
            print('Try to get state: {}'.format(self.dev_state))
            httpResponse.WriteResponseJSONOk(   headers = None,
                                                obj = self.dev_state )

        self.routeHandlers = [
            ( '/state', 'GET', httpHandlerTestGet)
        ]
        self.mws = MicroWebSrv(
            webPath='www/',
            routeHandlers=self.routeHandlers )

@MicroWebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    firstname = formData["firstname"]
    lastname  = formData["lastname"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
    """ % ( MicroWebSrv.HTMLEscape(firstname),
            MicroWebSrv.HTMLEscape(lastname) )
    httpResponse.WriteResponseOk( headers         = None,
                                  contentType     = "text/html",
                                  contentCharset = "UTF-8",
                                  content          = content )


@MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
    content = """\
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
    """
    content += "<h1>EDIT item with {} variable arguments</h1>"\
        .format(len(args))

    if 'index' in args :
        content += "<p>index = {}</p>".format(args['index'])

    if 'foo' in args :
        content += "<p>foo = {}</p>".format(args['foo'])

    content += """
        </body>
    </html>
    """
    httpResponse.WriteResponseOk( headers         = None,
                                  contentType     = "text/html",
                                  contentCharset = "UTF-8",
                                  content          = content )
