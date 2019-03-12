import machine
from network import WLAN
from utils import log

class WLANAgent:

    def __init__(self, ap_config=None, sta_config=None):
        self._wlan = None
        self.networks = {}
        self._sta_config = sta_config
        self._ap_config = ap_config

    def isActive(self):
        return self._wlan != None

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
        self.connect_to_ap()

    def connect_to_ap(self):
        if len(list(self.networks.items())) < 1:
            raise Exception("Need networks to connect to Wifi AP.")

        if self._wlan.mode() != WLAN.STA:
            raise Exception("Must in Station Mode to connect to Wifi AP.")

        existing_networks = self._wlan.scan()
        log('Found {}. existing wlan networks.'.format(len(existing_networks)))

        for network in existing_networks:
            (ssid, bssid, sec, channel, rssi) = network
            if ssid in self.networks:
                password = self.networks[ssid]
                self._wlan.connect(ssid, auth=(WLAN.WPA2, password))
                log('Connect to wifi {}'.format(ssid))
