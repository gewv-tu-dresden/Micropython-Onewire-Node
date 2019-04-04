import machine
from network import WLAN
from utils import log
from time import time, sleep

class WLANAgent:

    def __init__(self, ap_config=None, sta_config=None):
        self._wlan = None
        self.networks = {}
        self._sta_config = sta_config
        self._ap_config = ap_config

    def isActive(self):
        return self._wlan != None

    def isconnected(self):
        return self._wlan.isconnected()

    def activate_ap_mode(self, ssid, password):
        if self._ap_config is None:
            log('No config to init AP Mode.')
            return

        try:
            ssid = self._ap_config['ssid']
            password = self._ap_config['password']
        except KeyError:
            log('Need password or ssid to init Access Point.')
            return

        if self._wlan:
            self._wlan.deinit()
            self._wlan = None

        self._wlan = WLAN(
            mode=WLAN.AP,
            ssid=ssid,
            auth=(WLAN.WPA2, password),
        )

    def stop(self):
        if self._wlan:
            self._wlan.deinit()
            self._wlan = None

    def activate_sta_mode(self):
        if self._sta_config is None:
            log('No config to init STA Mode.')
            return

        try:
            self.networks = self._sta_config['wifi_networks']
        except KeyError:
            log('Need networks to init Wifi Station.')
            return

        if self._wlan:
            self._wlan.deinit()
            self._wlan = None

        self._wlan = WLAN(
            mode=WLAN.STA,
        )
        self._wlan.ifconfig(config="dhcp")
        self.connect_to_ap()

    def connect_to_ap(self):
        while not self._wlan.isconnected():
            try:
                if len(list(self.networks.items())) < 1:
                    raise Exception("Need networks to connect to Wifi AP.")

                if self._wlan.mode() != WLAN.STA:
                    raise Exception("Must in Station Mode to connect to Wifi AP.")

                existing_networks = self._wlan.scan()
                log('Found {}. existing wlan networks.'.format(len(existing_networks)))

                for network in existing_networks:
                    (ssid, bssid, sec, channel, rssi) = network
                    log('Try to connect to network {}'.format(ssid))
                    if ssid in self.networks:
                        password = self.networks[ssid]
                        self._wlan.connect(ssid, auth=(WLAN.WPA2, password))
                        break

                now = time()
                while not self._wlan.isconnected():
                    if (time()-now > 10):
                        raise Exception('Failed to connect to wlan {}. Timeout.'.format(self._wlan.ssid()))
                    sleep(0.3)

                (ip, subnet_mask, gateway, DNS_server) = self._wlan.ifconfig()
                log('Connect to wifi {}'.format(self._wlan.ssid()))
                log('IP: {}'.format(ip))
            except Exception as err:
                log(err)
                sleep(2)
