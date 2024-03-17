import aqUtils
import network
import ntptime
import machine
import utime

timeZoneOffset = 4

ap = network.WLAN(network.AP_IF)
ap.active(False)

aqUtils.do_connect()

try:
    ntptime.host = 'time1.google.com'
    t = ntptime.time()    
    tm = utime.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3] - timeZoneOffset, tm[4], tm[5], 0))
except:
    print('Failed to get ntp time.')

