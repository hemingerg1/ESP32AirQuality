from machine import Pin, SoftI2C, UART
import uasyncio
import gc
import time
import bme680
import bme680AQ
import pms5003
from microdot_asyncio import Microdot, Response, send_file
#import umail
#import secrets


# Initialize MicroDot
app = Microdot()
Response.default_content_type = 'text/html'

# Initialize BME680
bme_i2c = SoftI2C(scl=Pin(26), sda=Pin(27))
bme = bme680.BME680_I2C(i2c=bme_i2c)
#Initialize IAQ calculator
iaq_tracker = bme680AQ.IAQTracker(burn_in_cycles = 100)

# Intialize PMS5003
pms_uart = UART(1, tx=14, rx=12, baudrate=9600)
pin27 = Pin(13, Pin.OUT)
pm = pms5003.PMS5003(pms_uart, reset_pin=pin27)


def send_email(message):
    smtp = umail.SMTP('smtp.gmail.com', 587, username=secrets.email_address, password=secrets.email_password)
    smtp.to(secrets.email_address)
    smtp.send(message)
    smtp.quit()
    gc.collect()

data = {'tempc':0, 'tempf':[], 'hum':[], 'pres':0, 'gas_res':0, 'aq':[], 
        'pm10_std':0, 'pm25_std':0, 'pm100_std':0, 'pm10_env':[], 'pm25_env':[], 'pm100_env':[], 
        'pm3':0, 'pm5':0, 'pm10':0, 'pm25':0, 'pm50':0, 'pm100':0,
        'mem_used':0, 'mem_free':0, 'mem_tot':0, 'mem_usedp':[], 'time':[]}
data_lists = ['tempf', 'hum', 'aq', 'pm10_env', 'pm25_env', 'pm100_env', 'mem_usedp', 'time']

async def get_data(max_hist_length=30):
    data['tempc'] = round(bme.temperature, 2)
    data['tempf'].append(round((data['tempc'] * (9/5)) + 32, 1))
    data['hum'].append(round(bme.humidity, 1))
    data['pres'] = round(bme.pressure/1000, 3)
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

    for r in data_lists:
        if len(data[r]) > max_hist_length:
            data[r].pop(0)



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

@app.route('/clock')
async def clock_pg(request):
    if request.method == 'post':
        from machine import RTC
        rtc = RTC()
        print(request.form)
        year = request.form['year']
        month = request.form['month']
        day = request.form['day']
        hour = request.form['hour']
        min = request.form['min']
        dt = (year, month, day, 0, hour, min, 0, 0)
        rtc.datetime(dt)
    return send_file('static/html/clock.html')

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



async def update_readings(data_sample_time=10):
    while True:
        uasyncio.create_task(get_data())
        await uasyncio.sleep(data_sample_time)
    
async def main():
    data_task = uasyncio.create_task(update_readings())
    app_task = uasyncio.create_task(app.start_server(debug=True, port=80))
    await uasyncio.gather(data_task, app_task)
    
uasyncio.run(main())
    

########## BME680 #########
# sensor pin      ESP32 pin 
# Vin             3.3V
# GND             GND
# SCL             GPIO 26
# SDA             GPIO 27


######### PMS5003 #########
# sensor pin      ESP32 pin 
# Vcc             +5V
# GND             GND
# RXD             GPIO 14
# TXD             GPIO 12
# RESET           GPIO 13
