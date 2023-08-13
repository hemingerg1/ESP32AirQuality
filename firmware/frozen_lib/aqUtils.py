from time import sleep
import network
import secrets
import ulogger
from machine import RTC
import urequests
import uasyncio
import gc


################ logger ################
# Initialize Logger
class Clock(ulogger.BaseClock):
    def __init__(self):
        self.rtc = RTC()

    def __call__(self) -> str:
        y, m, d, _, h, mi, s, _ = self.rtc.datetime()
        return '%d-%d-%d %d:%d:%d' % (y, m, d, h, mi, s)

clock = Clock()

file_handler = ulogger.Handler(
    level=ulogger.INFO,
    fmt='&(time)% - &(level)% - &(msg)%',
    clock=clock,
    direction=ulogger.TO_FILE,
    file_name='log.txt',
    max_file_size=12288)

def get_logger(name=__name__):
    return ulogger.Logger(name, handlers=[file_handler])

log = get_logger()


################ telegram ################
# sends a message from telegram bot to the chat
async def sendTelegram(message):
    r = urequests.post(
        f'https://api.telegram.org/bot{secrets.TELEGRAM_TOKEN}/sendMessage?chat_id={secrets.TELEGRAM_CHAT_ID}&text={message}')
    r.close()
    log.info(f'Telegram sent. Message = "{message}"')
    gc.collect()
    return

# get the last massage in the chat sent to telegram bot
def getLastMessage():
    url = f'https://api.telegram.org/bot{secrets.TELEGRAM_TOKEN}/getUpdates?offset=-1'
    r = urequests.get(url)
    if r.json()['result']:
        text = r.json()['result'][-1]['message']['text']
        time = r.json()['result'][-1]['message']['date']
    else:
        text = ''
        time = 0
    r.close()
    gc.collect()
    return text, time


################ garage door ################
# closes garage door
async def closeGarageDoor(door):
    if door.value() == 1:
        uasyncio.create_task(sendTelegram('Door is open. Closing it now.'))
        ####### TO DO: need to figure out hardware side to impliment closing the door ############
        c = 0
        while door.value() == 1:
            if c >= 12:
                uasyncio.create_task(sendTelegram('Garage door did not close succesfully. Timed out.'))
                break
            await uasyncio.sleep(5)
            c += 1
        if door.value() == 0:
            uasyncio.create_task(sendTelegram('Garage door closed successfully'))
    else:
        uasyncio.create_task(sendTelegram('Door already closed. Doing nothing.'))
    return


################ WIFI ################
def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print('Connecting to Wifi...')
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('WIFI connected.')
    print('>>>>>>>>>>>>>>> IP address:', sta_if.ifconfig()[0], '<<<<<<<<<<<<<<<')


def reconnect():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)
    sleep(2)
    do_connect()


def internet_check(log=log):
    r = urequests.get('https://www.google.com')
    if r.status_code == 200:
        r.close()
    else:
        r.close()
        log.warn('No internet connection. Attempting to reconnect now.')
        reconnect()
        log.info('WIFI reconnected')


################ Influxdb ################
async def influxSend(data):
    r = urequests.post(url=secrets.INFLUX_URL, headers={'Authorization': secrets.INFLUX_TOKEN}, data=data)
    if r.status_code < 200 or r.status_code >= 300:
        code = r.json()['code']
        log.warn(f'Influx post unsuccessful. Error: "{code}"')
    r.close()
    gc.collect()
    return
