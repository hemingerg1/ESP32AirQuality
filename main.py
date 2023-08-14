from machine import Pin, SoftI2C, UART, RTC
from micropython import const
import uasyncio
import gc
import time
import bme680
import bme680AQ
import pms5003
from microdot_asyncio import Microdot, Response, send_file
import aqUtils

data_sample_time = const(60)  # frequency to take data readings, in seconds
max_hist_length = const(120)  # max number of data point to keep time to wait before alerting of door remaining open, in number of data samplings
door_alert_time = const(15)
pm_alert_level = const(50)  # if pm2.5 goes above this, sends telegram alert if air quality drops below this, sends telegram alert
aq_alert_level = const(70)
pm_alerted = False
aq_alerted = False
teleDoorClosing = False
last_message_time = 0

# Initialize Logger
log = aqUtils.get_logger()

# Initialize MicroDot
app = Microdot()
Response.default_content_type = 'text/html'

# Initialize BME680
bme_i2c = SoftI2C(scl=Pin(27), sda=Pin(26))
bme = bme680.BME680_I2C(i2c=bme_i2c)
# Initialize IAQ calculator
iaq_tracker = bme680AQ.IAQTracker(burn_in_cycles=100)
# applies an offset to BME680 temperature reading for calibration
temp_offset = -3.3

# Intialize PMS5003
pms_uart = UART(1, tx=14, rx=25, baudrate=9600)
pin27 = Pin(13, Pin.OUT)
pm = pms5003.PMS5003(pms_uart, reset_pin=pin27, active_mode=False,
                     interval_passive_mode=20, eco_mode=False)

# Intialize GPIO pins
# for doors, value of high or 1 means door is open
Ldoor = Pin(23, Pin.IN, Pin.PULL_UP)
Sdoor = Pin(22, Pin.IN, Pin.PULL_UP)
HOdoor = Pin(21, Pin.IN, Pin.PULL_UP)
HIdoor = Pin(19, Pin.IN, Pin.PULL_UP)
# pin for garage door opener
OpPin = Pin(18, Pin.OUT, value=0)


data = {'tempc': 0, 'tempf': [], 'hum': [], 'pres': 0, 'gas_res': 0, 'aq': [],
        'pm10_std': 0, 'pm25_std': 0, 'pm100_std': 0, 'pm10_env': [], 'pm25_env': [], 'pm100_env': [],
        'pm3': 0, 'pm5': 0, 'pm10': 0, 'pm25': 0, 'pm50': 0, 'pm100': 0,
        'mem_used': 0, 'mem_free': 0, 'mem_tot': 0, 'mem_usedp': [], 'time': [],
        'Ldoorsat': '', 'Ldoortime': 0, 'Sdoorsat': '', 'Sdoortime': 0,
        'HOdoorsat': '', 'HOdoortime': 0, 'HIdoorsat': '', 'HIdoortime': 0}
data_lists = ['tempf', 'hum', 'aq', 'pm10_env',
              'pm25_env', 'pm100_env', 'mem_usedp', 'time']
door_list = {'Ldoor': Ldoor, 'Sdoor': Sdoor,
             'HOdoor': HOdoor, 'HIdoor': HIdoor}


# updates data with latest readings
async def get_data():
    global max_hist_length, pm_alert_level, aq_alert_level, pm_alerted, aq_alerted, teleDoorClosing, last_message_time

    data['tempc'] = round(bme.temperature, 2) + temp_offset
    data['tempf'].append(round((data['tempc'] * (9/5)) + 32, 1))
    data['hum'].append(round(bme.humidity, 1))
    data['pres'] = round(bme.pressure/1000, 2)
    data['gas_res'] = bme.gas
    try:
        data['aq'].append(round(iaq_tracker.getIAQ(
            temp=data['tempc'], hum=data['hum'][-1], R_gas=data['gas_res'])))
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
    data['mem_usedp'].append(round(data['mem_used'] / data['mem_tot'], 2))

    if data['mem_usedp'][-1] >= 0.8:
        log.warn(
            f'Memory useage is high. Percent mem used = {data["mem_usedp"][-1]}')

    t = time.localtime()
    loc_tim = f'{t[3]}:{t[4]}:{t[5]}'
    data['time'].append(loc_tim)

    # delete data if too long
    for r in data_lists:
        if len(data[r]) > max_hist_length:
            data[r].pop(0)

    # check status of doors
    try:
        for d, p in door_list.items():
            if p.value() == 1 and data[f'{d}sat'] != 'open':  # door just opened
                data[f'{d}sat'] = 'open'
                data[f'{d}time'] = 0
            # door has been open
            elif p.value() == 1 and data[f'{d}sat'] == 'open':
                data[f'{d}time'] += 1
                if data[f'{d}time'] == door_alert_time:
                    if d == 'Ldoor':
                        m, t = aqUtils.getLastMessage()
                        last_message_time = t
                        uasyncio.create_task(aqUtils.sendTelegram('LARGE GARAGE DOOR has been left open.  Reply "c" to close.'))
                        await uasyncio.sleep(2)
                    elif d == 'Sdoor':
                        uasyncio.create_task(aqUtils.sendTelegram('SMALL GARAGE DOOR has been left open.'))
                        await uasyncio.sleep(2)
                    elif d == 'HOdoor':
                        uasyncio.create_task(aqUtils.sendTelegram('GARAGE\'S OUTSIDE WALK-IN DOOR has been left open.'))
                        await uasyncio.sleep(2)
                    elif d == 'HIdoor':
                        uasyncio.create_task(aqUtils.sendTelegram('GARAGE\'S INSIDE DOOR TO SHOP has been left open.'))
                        await uasyncio.sleep(2)
                # check for telegram request to close door
                elif d == 'Ldoor' and data[f'{d}time'] > door_alert_time:
                    m, t = aqUtils.getLastMessage()
                    m = m.lower()
                    if m == 'c' and t > last_message_time and teleDoorClosing == False:
                        teleDoorClosing = True
                        uasyncio.create_task(aqUtils.closeGarageDoor(door=Ldoor, opener_pin=OpPin))
                    last_message_time = t
            elif p.value() == 0 and data[f'{d}sat'] != 'closed':  # door just closed
                data[f'{d}sat'] = 'closed'
                data[f'{d}time'] = 0
                teleDoorClosing = False
    except:
        log.warn('Door check failed')

    # send telegram alert if PM is too high
    try:
        if data['pm25_env'][-1] is not None and data['pm25_env'][-1] > pm_alert_level:
            if pm_alerted == False:
                uasyncio.create_task(aqUtils.sendTelegram(
                    f'PM is high.  PM = {data["pm25_env"][-1]}'))
                pm_alerted = True
        elif data['pm25_env'][-1] is not None and data['pm25_env'][-1] < pm_alert_level - 5:
            pm_alerted = False
    except:
        log.warn('PM telegram alert failed')

    # send telegram alert if Air Quality is poor
    try:
        if len(data['aq']) > 0 and data['aq'][-1] < aq_alert_level:
            if aq_alerted == False:
                uasyncio.create_task(aqUtils.sendTelegram(
                    f'Air Quality is poor.  AQ = {data["aq"][-1]}'))
                aq_alerted = True
        elif len(data['aq']) > 0 and data['aq'][-1] > aq_alert_level + 10:
            aq_alerted = False
    except:
        log.warn('AQ telegram alert failed')

    # send data to influxDB
    try:
        if len(data['aq']) > 0:
            uasyncio.create_task(aqUtils.influxSend(f'Air Temperature={data["tempf"][-1]},AQ={data["aq"][-1]},GasRes={data["gas_res"]},PM25={data["pm25_env"][-1]}'))
        elif data['pm25_env'][-1] is not None:
            uasyncio.create_task(aqUtils.influxSend(f'Air Temperature={data["tempf"][-1]},GasRes={data["gas_res"]},PM25={data["pm25_env"][-1]}'))
    except:
        log.warn('Influx try failed.')

    return


###### Microdot web pages ######
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


@app.route('/log')
async def log_pg(request):
    return send_file('static/html/log.html')


@app.route('/clock', methods=['GET'])
async def clock_pg(request):
    return send_file('static/html/clock.html')


@app.route('/clock', methods=['POST'])
async def clock_set(request):
    year = int(request.form['year'])
    month = int(request.form['month'])
    day = int(request.form['day'])
    hour = int(request.form['hour'])
    minute = int(request.form['min'])
    dt = (year, month, day, 0, hour, minute, 0, 0)
    log.info(f'set real time clock to: {dt}')
    RTC().datetime(dt)
    return


# send RTC time in json
@app.route('/rtc')
async def tim(request):
    t = time.localtime()
    current_time = {'year': t[0], 'month': t[1],
                    'day': t[2], 'hour': t[3], 'min': t[4], 'sec': t[5]}
    return current_time


# send data to js script
@app.route('/data')
async def data_send(rquest):
    return data

# after each request collect garbage
@app.after_request
async def mem_collect(request, response):
    gc.collect()


# can use this route to shutdown the server
@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    log.info('Server shutdown by /shutdown route')
    return 'The server is shutting down...'


# sends the static files (html,css,javascript)
@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # don't allow moving up directories
        return 'Not found', 404
    return send_file('static/' + path)


# sends log file
@app.route('/log.txt')
async def logf(request):
    return send_file('log.txt')


# create async loop to update data
async def update_readings(data_sample_time=data_sample_time):
    l_count = 0
    while True:
        l_count += 1
        await uasyncio.create_task(get_data())
        await uasyncio.sleep(data_sample_time)
        if l_count >= 20:
            try:
                aqUtils.internet_check()
                l_count = 0
            except:
                log.warn('Internet check failed')


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
