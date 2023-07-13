import network
import secrets
import ntptime
import machine
import utime

timeZoneOffset = 4

ap = network.WLAN(network.AP_IF)
ap.active(False)

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
    
do_connect()

try:
    ntptime.host = 'time.google.com'
    t = ntptime.time()    
    tm = utime.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3] - timeZoneOffset, tm[4], tm[5], 0))
except:
    print('Failed to get ntp time.')

