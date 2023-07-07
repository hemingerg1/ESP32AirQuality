from machine import Pin, SoftI2C, UART
from micropython import const
import uasyncio
import gc
import time
import bme680
import bme680AQ
import pms5003
from microdot_asyncio import Microdot, Response, send_file
import secrets
import urequests

data_sample_time = const(15) # frequency to take data readings, in seconds
max_hist_length = const(30) # max number of data point to keep
door_alert_time = const(40) # time to wait before alerting of door remaining open, in number of data samplings
pm_alert_level = const(50) # if pm2.5 goes above this, sends telegram alert 
aq_alert_level = const(70) # if air quality drops below this, sends telegram alert
pm_alerted = False
aq_alerted = False
teleDoorClosed = False

# Initialize MicroDot
app = Microdot()
Response.default_content_type = 'text/html'

# Initialize BME680
bme_i2c = SoftI2C(scl=Pin(27), sda=Pin(26))
bme = bme680.BME680_I2C(i2c=bme_i2c)
# Initialize IAQ calculator
iaq_tracker = bme680AQ.IAQTracker(burn_in_cycles = 100)
# applies an offset to BME680 temperature reading for calibration
temp_offset = -3.3

# Intialize PMS5003
pms_uart = UART(1, tx=14, rx=25, baudrate=9600)
pin27 = Pin(13, Pin.OUT)
pm = pms5003.PMS5003(pms_uart, reset_pin=pin27, active_mode=False, interval_passive_mode=20, eco_mode=False)

# Intialize GPIO pins
## for doors, value of high or 1 means door is open
Ldoor = Pin(23, Pin.IN, Pin.PULL_UP)
Sdoor = Pin(22, Pin.IN, Pin.PULL_UP)
HOdoor = Pin(21, Pin.IN, Pin.PULL_UP)
HIdoor = Pin(19, Pin.IN, Pin.PULL_UP)


data = {'tempc':0, 'tempf':[], 'hum':[], 'pres':0, 'gas_res':0, 'aq':[], 
        'pm10_std':0, 'pm25_std':0, 'pm100_std':0, 'pm10_env':[], 'pm25_env':[], 'pm100_env':[], 
        'pm3':0, 'pm5':0, 'pm10':0, 'pm25':0, 'pm50':0, 'pm100':0,
        'mem_used':0, 'mem_free':0, 'mem_tot':0, 'mem_usedp':[], 'time':[],
        'Ldoorsat':'', 'Ldoortime':0, 'Sdoorsat':'', 'Sdoortime':0,
        'HOdoorsat':'', 'HOdoortime':0, 'HIdoorsat':'', 'HIdoortime':0}
data_lists = ['tempf', 'hum', 'aq', 'pm10_env', 'pm25_env', 'pm100_env', 'mem_usedp', 'time']
door_list = {'Ldoor':Ldoor, 'Sdoor':Sdoor, 'HOdoor':HOdoor, 'HIdoor':HIdoor}

# sends a message from telegram bot to the chat
def sendTelegram(message):
    r = urequests.post(f'https://api.telegram.org/bot{secrets.TELEGRAM_TOKEN}/sendMessage?chat_id={secrets.TELEGRAM_CHAT_ID}&text={message}')
    r.close()
    print(f'Telegram sent. Message = "{message}"')
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

# closes garage door
async def closeGarageDoor():
    global Ldoor
    if Ldoor.value() == 1:
        sendTelegram('Closing garage door now...')
        ####### TO DO: need to figure out hardware side to impliment closing the door ############
        c = 0
        while Ldoor.value() == 1:
            if c >= 12:
                sendTelegram('Garage door did not close succesfully. Timed out.')
                break
            await uasyncio.sleep(5)
            c += 1
        if Ldoor.value() == 0:
            sendTelegram('Garage door closed successfully')
    else:
        sendTelegram('Door already closed. Doing nothing.')
    return

# updates data with latest readings
async def get_data():
    global max_hist_length, pm_alert_level, aq_alert_level, pm_alerted, aq_alerted, teleDoorClosed

    data['tempc'] = round(bme.temperature, 2) + temp_offset
    data['tempf'].append(round((data['tempc'] * (9/5)) + 32, 1))
    data['hum'].append(round(bme.humidity, 1))
    data['pres'] = round(bme.pressure/1000, 2)
    data['gas_res'] = bme.gas
    try:
        data['aq'].append(round(iaq_tracker.getIAQ(temp=data['tempc'], hum=data['hum'][-1], R_gas=data['gas_res'])))
    except:
        pass
    data['pm10_std'] = pm.pm10_standard
    data['pm25_std'] = pm.pm25_standard
    data['pm100_std'] = pm.pm100_standard
    data['pm10_env'].append(pm.pm10_env)
    data['pm25_env'].append(pm.pm25_env)
    data['pm100_env'].append(pm.pm100_env)
    data['pm3'] = pm.particles_03um
    data['pm5'] = pm.particles_05um
    data['pm10'] = pm.particles_10um
    data['pm25'] = pm.particles_25um
    data['pm50'] = pm.particles_50um
    data['pm100'] = pm.particles_100um
    data['mem_used'] = round(gc.mem_alloc() / 1000, 1)
    data['mem_free'] = round(gc.mem_free() / 1000, 1)
    data['mem_tot'] = data['mem_used'] + data['mem_free']
    data['mem_usedp'].append(round(data['mem_used'] / data['mem_tot'] , 2))

    t = time.localtime()
    loc_tim = f'{t[3]}:{t[4]}:{t[5]}'
    data['time'].append(loc_tim)

    # delete data if too long
    for r in data_lists:
        if len(data[r]) > max_hist_length:
            data[r].pop(0)

    # check status of doors
    for d, p in door_list.items():
        if p.value() == 1 and data[f'{d}sat'] != 'open': # door just opened
            data[f'{d}sat'] = 'open'
            data[f'{d}time'] = 0
        elif p.value() == 1 and data[f'{d}sat'] == 'open': # door has been open
            data[f'{d}time'] += 1
            if data[f'{d}time'] == door_alert_time:
                if d == 'Ldoor':
                    sendTelegram('LARGE GARAGE DOOR has been left open.  Reply "c" to close.')
                    await uasyncio.sleep(2)
                elif d == 'Sdoor':
                    sendTelegram('SMALL GARAGE DOOR has been left open.')
                    await uasyncio.sleep(2)
                elif d == 'HOdoor':
                    sendTelegram('GARAGE\'S OUTSIDE WALK-IN DOOR has been left open.')
                    await uasyncio.sleep(2)
                elif d == 'HIdoor':
                    sendTelegram('GARAGE\'S INSIDE DOOR TO SHOP has been left open.')
                    await uasyncio.sleep(2)
            elif d == 'Ldoor' and data[f'{d}time'] > door_alert_time: # check for telegram request to close door
                m, t = getLastMessage()
                m = m.lower()
                if m == 'c' and t > time.time() - (data_sample_time * 2) and teleDoorClosed == False:
                    teleDoorClosed = True
                    uasyncio.create_task(closeGarageDoor())
        elif p.value() == 0 and data[f'{d}sat'] != 'closed': # door just closed
            data[f'{d}sat'] = 'closed'
            data[f'{d}time'] = 0
            teleDoorClosed = False

    # send telegram alert if PM is too high
    if data['pm25_env'][-1] is not None and data['pm25_env'][-1] > pm_alert_level:
        if not pm_alerted:
            sendTelegram(f'PM is high.  PM = {data["pm25_env"][-1]}')
            pm_alerted = True
    else:
        pm_alerted = False
    
    # send telegram alert if Air Quality is poor
    if len(data['aq']) > 0 and data['aq'][-1] < aq_alert_level:
        if not aq_alerted:
            sendTelegram(f'Air Quality is poor.  AQ = {data["aq"][-1]}')
            aq_alerted = True
    elif len(data['aq']) > 0 and data['aq'][-1] > aq_alert_level + 10:
        aq_alerted = False
     
    return


# Microdot web pages
@app.route('/')
async def home_pg(request):
    return send_file('static/html/home.html')

@app.route('/sensors')
async def sensors_pg(request):
    return send_file('static/html/sensors.html')

@app.route('/dash')
async def dash_pg(request):
    return send_file('static/html/dash.html')

@app.route('/cam')
async def cam_pg(request):
    return send_file('static/html/cam.html')

@app.route('/clock', methods=['GET'])
async def clock_pg(request):
    return send_file('static/html/clock.html')

@app.route('/clock', methods=['POST'])
async def clock_set(request):
    from machine import RTC
    year = int(request.form['year'])
    month = int(request.form['month'])
    day = int(request.form['day'])
    hour = int(request.form['hour'])
    minute = int(request.form['min'])
    dt = (year, month, day, 0, hour, minute, 0, 0)
    print(f'set real time clock to: {dt}')
    RTC().datetime(dt)
    return

#send RTC time in json
@app.route('/rtc')
async def tim(request):
    t = time.localtime()
    current_time = {'year': t[0], 'month': t[1], 'day': t[2], 'hour': t[3], 'min': t[4], 'sec': t[5]}
    return current_time

#send data to js script
@app.route('/data')
async def data_send(rquest):
    return data

@app.after_request
async def mem_collect(request, response):
    gc.collect()

# can use this route to shutdown the server
@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

# sends the static files (html,css,javascript)
@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # don't allow moving up directories
        return 'Not found', 404
    return send_file('static/' + path)


# create async loop to update data
async def update_readings(data_sample_time=data_sample_time):
    while True:
        await uasyncio.create_task(get_data())
        await uasyncio.sleep(data_sample_time)

# create main async loop   
async def main():
    data_task = uasyncio.create_task(update_readings())
    app_task = uasyncio.create_task(app.start_server(debug=False, port=80))
    await uasyncio.gather(data_task, app_task)
    
uasyncio.run(main())
    

########## BME680 #########
# sensor pin      ESP32 pin 
# Vin             3.3V
# GND             GND
# SCL             GPIO 27
# SDA             GPIO 26


######### PMS5003 #########
# sensor pin      ESP32 pin 
# Vcc             +5V
# GND             GND
# RXD             GPIO 14
# TXD             GPIO 25
# RESET           GPIO 13

##### can use to send email alerts
#import umail
#def send_email(message):
#    smtp = umail.SMTP('smtp.gmail.com', 587, username=secrets.EMAIL_ADDRESS, password=secrets.EMAIL_PASSWORD)
#    smtp.to(secrets.email_address)
#    smtp.send(message)
#    smtp.quit()
#    gc.collect()
