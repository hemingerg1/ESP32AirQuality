import io
import os
import network
import secrets

class logToFile(io.IOBase):
    def __init__(self):
        pass
 
    def write(self, data):
        with open("logfile.txt", mode="a") as f:
            f.write(data)
        return len(data)
 
# now your console text output is saved into file
os.dupterm(logToFile())

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
