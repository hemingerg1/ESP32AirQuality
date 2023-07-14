from time import sleep
import network
import secrets

SSID = secrets.WIFI_SSID
PASSWORD = secrets.WIFI_PASSWORD

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print('Connecting to Wifi...')
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            pass
    print('WIFI connected.')
    print('>>>>>>>>>>>>>>> IP address:', sta_if.ifconfig()[0], '<<<<<<<<<<<<<<<')

def reconnect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    sleep(2)
    do_connect()

def internet_check():
    import urequests
    r = urequests.get('https://www.google.com')
    if r.status_code == 200:
        r.close()
    else:
        r.close()
        import logger
        log = logger.get_logger()
        log.WARN('No internet connection. Attempting to reconnect now.')
        reconnect()
        log.INFO('WIFI reconnected')


   