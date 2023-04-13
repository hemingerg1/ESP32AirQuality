import network
import secrets

ap = network.WLAN(network.AP_IF)
ap.active(False)

SSID = secrets.wifi_ssid
SSI_PASSWORD = secrets.wifi_password

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print('Connecting to Wifi...')
        sta_if.connect(SSID, SSI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('WIFI connected.')
    print('>>>>>>>>>>>>>>> IP address:', sta_if.ifconfig()[0], '<<<<<<<<<<<<<<<')
    
do_connect()
