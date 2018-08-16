from microWebSrv import MicroWebSrv
from network import WLAN
from time import sleep

class Webserver():

    def __init__(self, dev_eui):
        self.wlan = None
        self.mws = MicroWebSrv(webPath='www/')
        self.dev_eui = dev_eui

    def start(self):
        print('Start wlan access point and webserver.')
        self.wlan = WLAN(mode=WLAN.AP, ssid="GEWV_LORA_NODE_" + self.dev_eui, auth=(WLAN.WPA2, "let_me_in"), channel=7, antenna=WLAN.INT_ANT)
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

@MicroWebSrv.route('/test')
def httpHandlerTestGet(httpClient, httpResponse):
    content = """
    <!DOCTYPE html>
    <html lang=en>
        <head>
            <meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = {}
            <br />
            <form action="/test" method="post" accept-charset="ISO-8859-1">
                First name: <input type="text" name="firstname"><br />
                Last name: <input type="text" name="lastname"><br />
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """.format(httpClient.GetIPAddr())

    httpResponse.WriteResponseOk(   headers = None,
                                    contentType = "text/html",
                                    contentCharset = "UTF-8",
                                    content = content )

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
